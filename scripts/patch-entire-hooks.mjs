#!/usr/bin/env node
/**
 * Idempotently ensures Entire's generated OpenCode & Pi hook shims attach an
 * asynchronous `error` listener to `stdin` before calling `.end(...)` so an
 * early-exiting hook subprocess cannot raise an unhandled EPIPE error.
 *
 * Run after `entire agent add opencode` or `entire agent add pi --force`.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function ensureOpencodeStdinGuard(filePath) {
  if (!fs.existsSync(filePath)) return false;
  const original = fs.readFileSync(filePath, "utf8");
  const unguarded =
    '        proc.on("error", () => resolve())\n' +
    '        proc.on("close", () => resolve())\n' +
    '        proc.stdin?.end(json + "\\n")';
  const guarded =
    '        proc.on("error", () => resolve())\n' +
    '        proc.on("close", () => resolve())\n' +
    '        proc.stdin?.on("error", () => {})\n' +
    '        proc.stdin?.end(json + "\\n")';

  if (original.includes(guarded)) return false;
  if (!original.includes(unguarded)) {
    throw new Error(`Unexpected callHook layout in ${filePath}; inspect manually.`);
  }
  fs.writeFileSync(filePath, original.replace(unguarded, guarded), "utf8");
  return true;
}

function ensurePiStdinGuard(filePath) {
  if (!fs.existsSync(filePath)) return false;
  const original = fs.readFileSync(filePath, "utf8");
  if (original.includes('child.stdin?.on("error"')) return false;
  const target = "        child.stdin?.end(JSON.stringify(data));";
  const replacement =
    '        child.stdin?.on("error", () => {});\n' +
    "        child.stdin?.end(JSON.stringify(data));";
  if (!original.includes(target)) {
    throw new Error(`Unexpected stdin.end layout in ${filePath}; inspect manually.`);
  }
  fs.writeFileSync(filePath, original.replace(target, replacement), "utf8");
  return true;
}

const checkOnly = process.argv.includes("--check");
const opencodeFile = path.join(repoRoot, ".opencode", "plugin", "entire.ts");
const piFile = path.join(repoRoot, ".pi", "extensions", "entire", "index.ts");

if (checkOnly) {
  for (const [label, filePath, snippet] of [
    ["OpenCode callHook", opencodeFile, 'proc.stdin?.on("error"'],
    ["Pi hook runner", piFile, 'child.stdin?.on("error"'],
  ]) {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, "utf8");
      if (!content.includes(snippet)) {
        console.error(`[FAIL] ${label} (${filePath}) missing ${snippet} guard (run: node scripts/patch-entire-hooks.mjs)`);
        process.exit(1);
      }
    }
  }
  console.log("[PASS] Entire hook shims guard async stdin EPIPE.");
  process.exit(0);
}

const patchedOpencode = ensureOpencodeStdinGuard(opencodeFile);
const patchedPi = ensurePiStdinGuard(piFile);
console.log(
  `patch-entire-hooks: opencode=${patchedOpencode ? "patched" : "already-guarded"}, pi=${patchedPi ? "patched" : "already-guarded"}`,
);
