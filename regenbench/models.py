from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class TaskSpec:
    id: str
    test_command: list[str]
    regenerate_command: list[str]
    canonical_sources: list[str]
    generated_artifacts: list[str]

    @classmethod
    def load(cls, path: Path) -> "TaskSpec":
        raw = json.loads(path.read_text())
        return cls(
            id=raw["id"],
            test_command=list(raw["test_command"]),
            regenerate_command=list(raw["regenerate_command"]),
            canonical_sources=list(raw.get("canonical_sources", [])),
            generated_artifacts=list(raw.get("generated_artifacts", [])),
        )


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float

    @property
    def passed(self) -> bool:
        return self.returncode == 0


@dataclass
class EvaluationResult:
    task_id: str
    workspace: str
    changed_files_before_regen: list[str]
    canonical_sources_touched: list[str]
    generated_artifacts_touched: list[str]
    pre_regen_test: CommandResult
    regeneration: CommandResult
    post_regen_test: CommandResult | None
    regeneration_survived: bool
    generated_only_repair: bool
    source_of_truth_repair: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
