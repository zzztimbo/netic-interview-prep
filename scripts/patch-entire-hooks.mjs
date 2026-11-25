#!/usr/bin/env node
/**
 * Idempotently ensures Entire's generated OpenCode & Pi hook shims attach an
 * asynchronous `error` listener to `stdin` before every `.stdin?.end(...)` call
 * so an early-exiting hook subprocess cannot raise an unhandled EPIPE error.
 *
 * Run after `entire agent add opencode` or `entire agent add pi --force`.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function hasGuardBeforeEveryStdinEnd(content) {
  const lines = content.split("\n");
  let foundAny = false;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(".stdin?.end(")) {
      foundAny = true;
      const windowStart = Math.max(0, i - 3);
      const preceding = lines.slice(windowStart, i).join("\n");
      if (!preceding.includes('.stdin?.on("error"')) {
        return { ok: false, line: i + 1 };
      }
    }
  }
  return { ok: foundAny, line: foundAny ? null : 0 };
}

function patchAllStdinEnds(filePath) {
  if (!fs.existsSync(filePath)) return false;
  const lines = fs.readFileSync(filePath, "utf8").split("\n");
  let changed = false;
  const out = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const match = line.match(/^(\s*)(\w+)\.stdin\?\.end\(/);
    if (match) {
      const indent = match[1];
      const handle = match[2];
      const windowStart = Math.max(0, out.length - 3);
      const preceding = out.slice(windowStart).join("\n");
      if (!preceding.includes(`${handle}.stdin?.on("error"`)) {
        out.push(`${indent}${handle}.stdin?.on("error", () => {})`);
        changed = true;
      }
    }
    out.push(line);
  }

  if (changed) {
    fs.writeFileSync(filePath, out.join("\n"), "utf8");
  }
  const verify = hasGuardBeforeEveryStdinEnd(out.join("\n"));
  if (!verify.ok) {
    throw new Error(`Verification failed in ${filePath} near line ${verify.line}`);
  }
  return changed;
}

const checkOnly = process.argv.includes("--check");
const targets = [
  ["OpenCode plugin", path.join(repoRoot, ".opencode", "plugin", "entire.ts")],
  ["Pi extension", path.join(repoRoot, ".pi", "extensions", "entire", "index.ts")],
];

if (checkOnly) {
  for (const [label, filePath] of targets) {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, "utf8");
      const check = hasGuardBeforeEveryStdinEnd(content);
      if (!check.ok) {
        console.error(
          `[FAIL] ${label} (${filePath}:${check.line}) has unguarded .stdin?.end(...) call (run: node scripts/patch-entire-hooks.mjs)`,
        );
        process.exit(1);
      }
    }
  }
  console.log("[PASS] Every .stdin?.end(...) call in Entire hook shims is guarded against EPIPE.");
  process.exit(0);
}

for (const [label, filePath] of targets) {
  const updated = patchAllStdinEnds(filePath);
  console.log(`${label}: ${updated ? "patched" : "already-guarded"}`);
}
