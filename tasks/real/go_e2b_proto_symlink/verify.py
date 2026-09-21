from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
PACKAGE = ROOT / "internal" / "gen" / "envd" / "filesystem"
TEST_FILE = PACKAGE / "regenbench_symlink_test.go"

TEST_SOURCE = r'''package filesystem

import "testing"

func TestRegenBenchSymlinkEnum(t *testing.T) {
    if got := int32(FileType_FILE_TYPE_SYMLINK); got != 3 {
        t.Fatalf("FileType_FILE_TYPE_SYMLINK = %d, want 3", got)
    }
}
'''


def main() -> int:
    if not PACKAGE.exists():
        print(f"missing generated package: {PACKAGE}", file=sys.stderr)
        return 2
    if TEST_FILE.exists():
        print(f"refusing to overwrite existing file: {TEST_FILE}", file=sys.stderr)
        return 2

    TEST_FILE.write_text(TEST_SOURCE)
    try:
        proc = subprocess.run(
            ["go", "test", "./internal/gen/envd/filesystem", "-run", "TestRegenBenchSymlinkEnum", "-count=1"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return proc.returncode
    finally:
        TEST_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
