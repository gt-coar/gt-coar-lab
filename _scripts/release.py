"""standalone script for generating releases"""
# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.resolve()

# the version we're trying to release
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

# the full changelog
CHANGELOG = ROOT / "CHANGELOG.md"

# the tag we will create
TAG = f"v{VERSION}"

# a gross directory made from our dist artifacts
ARTIFACTS = ROOT / "artifacts"

# the SHA256 files
ARTIFACT_HASHES = sorted(ARTIFACTS.rglob(f"*{VERSION}*.sha256"))

# the base installers
INSTALLERS = [
    hashfile.parent / hashfile.name.replace(".sha256", "")
    for hashfile in ARTIFACT_HASHES
]

INSTALLERS = [installer for installer in INSTALLERS if installer.exists()]

# the concatenated shasums
SHA256SUMS = ROOT / "SHA256SUMS"


def make_notes():
    """generate release notes"""
    chunks = CHANGELOG.read_text(encoding="utf-8").split("---")
    notes = chunks[1].strip()
    assert f"## {VERSION}" in notes
    return notes


def make_hashsums():
    """collect all the hashfiles into one"""
    lines = []
    print(ARTIFACTS, flush=True)
    for hashfile in ARTIFACT_HASHES:
        print("...", hashfile, flush=True)
        lines += [hashfile.read_text(encoding="utf-8").strip()]

    hashsums = "\n".join(lines).strip()
    assert hashsums, "no sums"
    print(hashsums, flush=True)
    return hashsums


def release():
    """use the github CLI to create the release

    relies on GITHUB_TOKEN being set
    """
    assert INSTALLERS, "no installers"

    hashsums = make_hashsums()
    notes = make_notes()

    assert hashsums, "no hashsums"
    assert notes, "no notes"

    SHA256SUMS.write_text(hashsums, encoding="utf-8")

    args = [
        "gh",
        "release",
        "create",
        "--title",
        TAG,
        "--target",
        TAG,
        "--draft",
        "--notes",
        notes,
        SHA256SUMS,
        *INSTALLERS,
    ]

    print(args, flush=True)

    if os.environ.get("GITHUB_TOKEN", "").strip():
        return subprocess.call([*map(str, args)])

    return 0


if __name__ == "__main__":
    sys.exit(release())
