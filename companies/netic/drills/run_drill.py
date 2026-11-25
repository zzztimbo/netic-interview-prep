#!/usr/bin/env python3
"""CLI runner for Netic candidate debugging drills.

Examples:
    python3 companies/netic/drills/run_drill.py 1
    python3 companies/netic/drills/run_drill.py --solution 1
"""

from __future__ import annotations

import argparse
import importlib
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from companies.netic.drills.checks import DRILL_REGISTRY  # noqa: E402


def run_single(drill_id: int, use_solution: bool) -> int:
    module_stem, checker = DRILL_REGISTRY[drill_id]
    pkg = (
        "companies.netic.drills.reference_solutions"
        if use_solution
        else "companies.netic.drills.problems"
    )
    mod = importlib.import_module(f"{pkg}.{module_stem}")

    label = "REFERENCE SOLUTION" if use_solution else "CANDIDATE PROBLEM"
    print(f"=== Drill #{drill_id} ({label}): {module_stem}.py ===")
    if mod.__doc__:
        print(mod.__doc__.strip())
        print("-" * 64)

    failures = checker(mod)
    if not failures:
        print(f"[PASS] Drill #{drill_id}: all acceptance checks passed.")
        return 0

    print(f"[FAIL] Drill #{drill_id}: {len(failures)} check(s) failing:")
    for idx, item in enumerate(failures, start=1):
        print(f"  {idx}. {item}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Netic debugging drill checks.")
    parser.add_argument(
        "drill",
        type=int,
        choices=sorted(DRILL_REGISTRY.keys()),
        help="Drill number to verify (1-4).",
    )
    parser.add_argument(
        "--solution",
        action="store_true",
        help="Verify the reference solution instead of the candidate problem file.",
    )
    args = parser.parse_args(argv)
    return run_single(args.drill, use_solution=args.solution)


if __name__ == "__main__":
    sys.exit(main())
