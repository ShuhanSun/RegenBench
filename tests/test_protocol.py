from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from regenbench.evaluator import evaluate
from regenbench.models import TaskSpec

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tasks" / "demo_python_codegen" / "repo"
TASK = TaskSpec.load(ROOT / "tasks" / "demo_python_codegen" / "task.json")


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def init_repo(path: Path) -> None:
    run(["git", "init", "-q"], path)
    run(["git", "config", "user.email", "regenbench@example.invalid"], path)
    run(["git", "config", "user.name", "RegenBench Test"], path)
    run(["git", "add", "."], path)
    commit = run(["git", "commit", "-qm", "baseline"], path)
    if commit.returncode != 0:
        raise RuntimeError(commit.stderr)


class ProtocolTest(unittest.TestCase):
    def test_generated_only_patch_fails_after_regeneration(self) -> None:
        with tempfile.TemporaryDirectory(prefix="regenbench-test-bad-") as td:
            workspace = Path(td) / "repo"
            shutil.copytree(BASE, workspace)
            init_repo(workspace)

            generated = workspace / "generated" / "user_model.py"
            generated.write_text(generated.read_text().rstrip() + "\n    email_verified: bool\n")

            result = evaluate(TASK, workspace)
            self.assertTrue(result.pre_regen_test.passed)
            self.assertFalse(result.regeneration_survived)
            self.assertTrue(result.generated_only_repair)
            self.assertFalse(result.source_of_truth_repair)

    def test_source_of_truth_patch_survives_regeneration(self) -> None:
        with tempfile.TemporaryDirectory(prefix="regenbench-test-good-") as td:
            workspace = Path(td) / "repo"
            shutil.copytree(BASE, workspace)
            init_repo(workspace)

            schema = workspace / "schema" / "user.json"
            data = json.loads(schema.read_text())
            data["fields"].append({"name": "email_verified", "type": "bool"})
            schema.write_text(json.dumps(data, indent=2) + "\n")
            regen = run(["python", "tools/generate.py"], workspace)
            self.assertEqual(regen.returncode, 0, regen.stderr)

            result = evaluate(TASK, workspace)
            self.assertTrue(result.pre_regen_test.passed)
            self.assertTrue(result.regeneration_survived)
            self.assertFalse(result.generated_only_repair)
            self.assertTrue(result.source_of_truth_repair)


if __name__ == "__main__":
    unittest.main()
