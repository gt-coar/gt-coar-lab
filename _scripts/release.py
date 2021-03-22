"""standalone script for generating releases"""
# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

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

# how many times to try the real release
RETRIES = 10


def make_notes():
    """generate release notes"""
    chunks = CHANGELOG.read_text(encoding="utf-8").split("---")
    notes = chunks[1].strip()
    assert f"## {VERSION}" in notes
    return notes


def make_hashsums():
    """collect all the hashfiles into one"""
    LOG.info(f"artifacts {ARTIFACTS}")
    lines = []
    for hashfile in ARTIFACT_HASHES:
        LOG.info(f"... {hashfile}")
        lines += [hashfile.read_text(encoding="utf-8").strip()]

    hashsums = "\n".join(lines).strip()
    assert hashsums, "no sums"
    LOG.info("hashsums {hashsums}")
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
        TAG,
        "--draft",
        "--notes",
        notes,
        SHA256SUMS,
        *INSTALLERS,
    ]

    LOG.info("Release args %s", args)

    status_code = 0

    if os.environ.get("GITHUB_TOKEN", "").strip():
        status_code = 1
        LOG.warn(f"Trying to deploy {RETRIES} times...")
        for i in range(RETRIES):
            LOG.warn(f"... START attempt {i + 1} of {RETRIES}")
            status_code = subprocess.call([*map(str, args)])
            if status_code != 0:
                LOG.error(f"... FAIL attempt {i + 1} of {RETRIES}, waiting 10s...")
                time.sleep(10)

    return status_code


if __name__ == "__main__":
    sys.exit(release())
