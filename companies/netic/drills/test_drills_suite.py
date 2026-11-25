"""Automated test suite verifying both buggy drill reproductions and reference fixes."""

from __future__ import annotations

import importlib
import pathlib
import subprocess
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from companies.netic.drills.checks import DRILL_REGISTRY  # noqa: E402


class NeticDrillsVerificationTests(unittest.TestCase):
    def test_unedited_problems_reproduce_intended_bugs(self) -> None:
        """Every candidate problem module must deterministically fail before fixing."""
        for drill_id, (stem, checker) in DRILL_REGISTRY.items():
            with self.subTest(drill_id=drill_id, module=stem):
                problem_mod = importlib.import_module(
                    f"companies.netic.drills.problems.{stem}"
                )
                failures = checker(problem_mod)
                self.assertGreaterEqual(
                    len(failures),
                    2,
                    f"Problem drill #{drill_id} ({stem}) should reproduce >=2 bugs, got {failures!r}",
                )

    def test_reference_solutions_pass_all_checks(self) -> None:
        """Every reference solution module must pass 100% of acceptance checks."""
        for drill_id, (stem, checker) in DRILL_REGISTRY.items():
            with self.subTest(drill_id=drill_id, module=stem):
                solution_mod = importlib.import_module(
                    f"companies.netic.drills.reference_solutions.{stem}"
                )
                failures = checker(solution_mod)
                self.assertEqual(
                    failures,
                    [],
                    f"Reference solution #{drill_id} ({stem}) failed checks: {failures!r}",
                )

    def test_problem_files_contain_no_spoiler_comments(self) -> None:
        """Candidate files must not contain '# BUG' spoiler comments."""
        problems_dir = REPO_ROOT / "companies" / "netic" / "drills" / "problems"
        for py_file in sorted(problems_dir.glob("drill_*.py")):
            text = py_file.read_text(encoding="utf-8")
            self.assertNotIn("# BUG", text.upper(), f"Spoiler comment found in {py_file.name}")

    def test_cli_runner_exit_codes(self) -> None:
        """CLI exits non-zero on buggy problem and zero on --solution."""
        runner = REPO_ROOT / "companies" / "netic" / "drills" / "run_drill.py"

        fail_proc = subprocess.run(
            [sys.executable, str(runner), "1"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(fail_proc.returncode, 1)
        self.assertIn("[FAIL]", fail_proc.stdout)

        pass_proc = subprocess.run(
            [sys.executable, str(runner), "--solution", "1"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(pass_proc.returncode, 0)
        self.assertIn("[PASS]", pass_proc.stdout)


if __name__ == "__main__":
    unittest.main()
