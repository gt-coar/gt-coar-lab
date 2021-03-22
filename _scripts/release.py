"""standalone script for generating releases"""
# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import logging
import shutil
import sys
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

# where we put the release stuff
RELEASE = ROOT / "release"

# extracted from CHANGELOG
NOTES = RELEASE / "NOTES.md"

# where we put the actual release artifacts
RELEASE_ARTIFACTS = RELEASE / "artifacts"

# the concatenated shasums
SHA256SUMS = RELEASE_ARTIFACTS / "SHA256SUMS"


def make_notes():
    """generate release notes"""
    chunks = CHANGELOG.read_text(encoding="utf-8").split("---")
    notes = chunks[1].strip()
    assert f"## {VERSION}" in notes
    LOG.info(f"notes {notes}")
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
    LOG.info(f"hashsums {hashsums}")
    return hashsums


def make_artifacts():
    LOG.warning(f"... ensuring {RELEASE_ARTIFACTS} exists")
    RELEASE_ARTIFACTS.mkdir(exist_ok=True, parents=True)

    for artifact in ARTIFACTS:
        LOG.warning(f"... copying {artifact.name}")
        shutil.copy2(artifact, RELEASE_ARTIFACTS / artifact.name)
        LOG.warning(f"... OK {artifact.name}")


def release():
    """prepare a release folder with the structure

    release/
        NOTES.md
        artifacts/
            SHA256SUMS
            <all the goods>
    """
    assert INSTALLERS, "no installers"

    make_artifacts()

    hashsums = make_hashsums()
    notes = make_notes()

    assert hashsums, "no hashsums"
    assert notes, "no notes"

    SHA256SUMS.write_text(hashsums, encoding="utf-8")
    NOTES.write_text(notes, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(release())
