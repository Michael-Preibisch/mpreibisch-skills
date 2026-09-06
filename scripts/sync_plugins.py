#!/usr/bin/env python3
"""Copy shared runtime files into the separately installable Claude package."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "plugins/mpreibisch-codex"
DESTINATION = ROOT / "plugins/mpreibisch-claude"


def main():
    for directory in ("skills", "scripts", "bridge"):
        for source in (SOURCE / directory).rglob("*"):
            if not source.is_file() or "__pycache__" in source.parts:
                continue
            relative = source.relative_to(SOURCE)
            if relative.as_posix() == "bridge/host.json":
                continue
            target = DESTINATION / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    print("Shared runtime files synchronized.")


if __name__ == "__main__":
    main()
