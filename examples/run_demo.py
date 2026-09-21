from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "tasks" / "demo_python_codegen" / "repo"
TASK = ROOT / "tasks" / "demo_python_codegen" / "task.json"


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def init_repo(path: Path):
    run(["git", "init", "-q"], path)
    run(["git", "config", "user.email", "regenbench@example.invalid"], path)
    run(["git", "config", "user.name", "RegenBench Demo"], path)
    run(["git", "add", "."], path)
    run(["git", "commit", "-qm", "baseline"], path)


def apply_bad_patch(path: Path):
    p = path / "generated" / "user_model.py"
    text = p.read_text().rstrip() + "\n    email_verified: bool\n"
    p.write_text(text)


def apply_good_patch(path: Path):
    p = path / "schema" / "user.json"
    data = json.loads(p.read_text())
    data["fields"].append({"name": "email_verified", "type": "bool"})
    p.write_text(json.dumps(data, indent=2) + "\n")
    run(["python", "tools/generate.py"], path)


def evaluate(label: str, patcher):
    with tempfile.TemporaryDirectory(prefix=f"regenbench-{label}-") as td:
        workspace = Path(td) / "repo"
        shutil.copytree(BASE, workspace)
        init_repo(workspace)
        patcher(workspace)
        proc = subprocess.run(
            [
                "python", "-m", "regenbench", "evaluate",
                "--task", str(TASK),
                "--workspace", str(workspace),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"\n=== {label.upper()} PATCH ===")
        print(proc.stdout)


if __name__ == "__main__":
    evaluate("bad", apply_bad_patch)
    evaluate("good", apply_good_patch)
