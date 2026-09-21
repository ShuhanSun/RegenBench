from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass
class AggregateMetrics:
    tasks: int
    pre_regen_pass_rate: float
    post_regen_pass_rate: float
    regeneration_survival_rate: float
    generated_only_repair_rate: float
    source_of_truth_repair_rate: float

    def to_dict(self):
        return asdict(self)


def aggregate(results: Iterable[dict]) -> AggregateMetrics:
    rows = list(results)
    n = len(rows)
    if n == 0:
        return AggregateMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0)

    pre = [r for r in rows if r["pre_regen_test"]["returncode"] == 0]
    post = [
        r for r in rows
        if r.get("post_regen_test") is not None
        and r["post_regen_test"]["returncode"] == 0
    ]
    survived = [r for r in rows if r.get("regeneration_survived")]
    generated_only = [r for r in pre if r.get("generated_only_repair")]
    source_repair = [r for r in rows if r.get("source_of_truth_repair")]

    return AggregateMetrics(
        tasks=n,
        pre_regen_pass_rate=len(pre) / n,
        post_regen_pass_rate=len(post) / n,
        regeneration_survival_rate=(len(survived) / len(pre)) if pre else 0.0,
        generated_only_repair_rate=(len(generated_only) / len(pre)) if pre else 0.0,
        source_of_truth_repair_rate=len(source_repair) / n,
    )
