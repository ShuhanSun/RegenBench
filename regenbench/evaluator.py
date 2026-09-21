from __future__ import annotations

import fnmatch
import subprocess
import time
from pathlib import Path

from .models import CommandResult, EvaluationResult, TaskSpec


def _expand_command(command: list[str], task: TaskSpec, workspace: Path) -> list[str]:
    replacements = {
        "{task_dir}": task.task_dir,
        "{workspace}": str(workspace),
    }
    return [
        arg.replace("{task_dir}", replacements["{task_dir}"]).replace("{workspace}", replacements["{workspace}"])
        for arg in command
    ]


def _run(command: list[str], cwd: Path) -> CommandResult:
    started = time.monotonic()
    proc = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return CommandResult(
        command=command,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
        duration_seconds=round(time.monotonic() - started, 4),
    )


def _changed_files(workspace: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=workspace,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        return []
    files: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path)
    return sorted(set(files))


def _matches_any(path: str, patterns: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        pattern = pattern.replace("\\", "/")
        if fnmatch.fnmatch(normalized, pattern):
            return True
        if pattern.endswith("/**") and normalized.startswith(pattern[:-3].rstrip("/") + "/"):
            return True
    return False


def evaluate(task: TaskSpec, workspace: Path) -> EvaluationResult:
    workspace = workspace.resolve()
    changed = _changed_files(workspace)
    canonical = [p for p in changed if _matches_any(p, task.canonical_sources)]
    generated = [p for p in changed if _matches_any(p, task.generated_artifacts)]

    test_command = _expand_command(task.test_command, task, workspace)
    regenerate_command = _expand_command(task.regenerate_command, task, workspace)

    pre = _run(test_command, workspace)
    regen = _run(regenerate_command, workspace)
    post = _run(test_command, workspace) if regen.passed else None

    survived = bool(pre.passed and regen.passed and post and post.passed)
    generated_only = bool(pre.passed and generated and not canonical)
    source_repair = bool(survived and canonical)

    return EvaluationResult(
        task_id=task.id,
        workspace=str(workspace),
        changed_files_before_regen=changed,
        canonical_sources_touched=canonical,
        generated_artifacts_touched=generated,
        pre_regen_test=pre,
        regeneration=regen,
        post_regen_test=post,
        regeneration_survived=survived,
        generated_only_repair=generated_only,
        source_of_truth_repair=source_repair,
    )
