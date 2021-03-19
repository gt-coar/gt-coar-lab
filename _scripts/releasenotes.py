"""standalone script for generating release notes"""
# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent

VERSION = ROOT / "VERSION"
CHANGELOG = ROOT / "CHANGELOG.md"


def notes():
    """"""
    version = VERSION.read_text(encoding="utf-8")
    chunks = CHANGELOG.read_text(encoding="utf-8").split("---")
    this_release = chunks[1].strip()
    assert f"## {version}" in this_release
    return this_release


if __name__ == "__main__":
    print(notes())
    sys.exit(0)
