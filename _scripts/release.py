"""standalone script for generating releases"""
# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import logging
import math
import os
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
GIT_REF = os.environ["GIT_REF"].split("/")[-1]

# artifact size (in megabytes, slightly smaller for rounding)
MAX_ARTIFACT_MBS = 1949


def make_notes():
    """generate release notes"""
    chunks = CHANGELOG.read_text(encoding="utf-8").split("---")
    notes = chunks[1].strip()
    assert f"## {VERSION}" in notes
    LOG.info(f"notes {notes}")
    NOTES.write_text(notes, encoding="utf-8")
    return NOTES


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
    SHA256SUMS.write_text(hashsums, encoding="utf-8")
    return SHA256SUMS


def make_artifacts():
    LOG.warning(f"... collecting release artifacts to {RELEASE_ARTIFACTS}")
    RELEASE_ARTIFACTS.mkdir(exist_ok=True, parents=True)

    yield make_hashsums()
    yield make_notes()

    for installer in INSTALLERS:
        stat = installer.stat()
        mbs = int(stat.st_size / 1e6)
        LOG.warning(f"{mbs}mb {installer.name}")
        if mbs < MAX_ARTIFACT_MBS:
            LOG.warning("... will be uploaded as-is")
            yield installer
            continue
        LOG.warning(
            f"... >{MAX_ARTIFACT_MBS}mb, will split into "
            f"~{math.ceil(mbs / MAX_ARTIFACT_MBS)} .z* files"
        )
        args = [
            "zip",
            "-9",
            "--no-dir-entries",
            "--split-size",
            f"{MAX_ARTIFACT_MBS}m",
            RELEASE_ARTIFACTS / f"{installer.stem}.zip",
            installer,
        ]
        str_args = [*map(str, args)]
        LOG.warning(f"""... ... {" ".join(str_args)}""")
        subprocess.check_call(str_args)
        all_zipped = sorted(RELEASE_ARTIFACTS.glob(f"{installer.stem}.z*"))
        if not all_zipped:
            raise ValueError(f"... Failed to split {installer}")
        for zipped in all_zipped:
            LOG.warning(
                f"... ... ... {int(zipped.stat().st_size / 1e6)}mb {zipped.name}"
            )
            yield zipped


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
            f"tag={GIT_REF}",
            f"filename={artifact.relative_to(ROOT)}",
        ]

        LOG.warning(f"""... args before token {args}""")

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

    for artifact in make_artifacts():
        statuses = [0]
        statuses += [upload_one(artifact)]

    return max(statuses)


if __name__ == "__main__":
    sys.exit(release())
