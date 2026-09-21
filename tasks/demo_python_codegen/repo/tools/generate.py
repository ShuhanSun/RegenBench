from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema" / "user.json"
OUTPUT = ROOT / "generated" / "user_model.py"

schema = json.loads(SCHEMA.read_text())
fields = schema["fields"]
lines = [
    "# AUTO-GENERATED FILE. DO NOT EDIT DIRECTLY.",
    "from dataclasses import dataclass",
    "",
    "@dataclass",
    f"class {schema['class_name']}:",
]
for field in fields:
    lines.append(f"    {field['name']}: {field['type']}")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(lines) + "\n")
print(f"generated {OUTPUT.relative_to(ROOT)}")
