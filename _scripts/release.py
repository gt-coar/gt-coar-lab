"""standalone script for generating releases"""
# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import logging
import os
import shutil
import subprocess
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

# the github token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# the tag
TAG = (
    subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
    .decode("utf-8")
    .strip()
)


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

    for installer in INSTALLERS:
        LOG.warning(f"... copying {installer.name}")
        dest = RELEASE_ARTIFACTS / installer.name
        if not dest.exists():
            shutil.copy2(installer, dest)
        LOG.warning(f"... OK {installer.name}")


def upload_one(artifact) -> int:
    LOG.warning(f"Uploading {artifact.name}...")
    status = 0
    for i in range(3):
        LOG.warning(f"... {i+1} of 3")
        args = [
            "bash",
            HERE / "upload-github-release-asset.sh",
            "owner=gt-coar",
            "repo=gt-coar-lab",
            f"tag={TAG}",
            f"filename={artifact.relative_to(ROOT)}",
        ]

        LOG.warning(f"""... args before token {" ".join(args)}""")

        if GITHUB_TOKEN:
            args += [f"github_api_token={GITHUB_TOKEN}"]
            status = subprocess.call([*map(str, args)])

        if status == 0:
            return status
    return status


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

    statuses = [0]

    for artifact in RELEASE_ARTIFACTS.glob("*"):
        statuses += [upload_one(artifact)]

    return max(statuses)


if __name__ == "__main__":
    sys.exit(release())
