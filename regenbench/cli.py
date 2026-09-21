from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluator import evaluate
from .models import TaskSpec
from .aggregate import aggregate


def main() -> int:
    parser = argparse.ArgumentParser(prog="regenbench")
    sub = parser.add_subparsers(dest="command", required=True)

    evaluate_parser = sub.add_parser("evaluate", help="evaluate one agent-modified worktree")
    evaluate_parser.add_argument("--task", required=True, type=Path)
    evaluate_parser.add_argument("--workspace", required=True, type=Path)
    evaluate_parser.add_argument("--output", type=Path)

    aggregate_parser = sub.add_parser("aggregate", help="aggregate JSON evaluation results")
    aggregate_parser.add_argument("results", nargs="+", type=Path)

    args = parser.parse_args()
    if args.command == "evaluate":
        task = TaskSpec.load(args.task)
        result = evaluate(task, args.workspace)
        payload = json.dumps(result.to_dict(), indent=2)
        if args.output:
            args.output.write_text(payload + "\n")
        print(payload)
        return 0 if result.regeneration_survived else 1
    if args.command == "aggregate":
        rows = [json.loads(path.read_text()) for path in args.results]
        print(json.dumps(aggregate(rows).to_dict(), indent=2))
        return 0
    return 2
