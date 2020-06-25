# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

""" standalone script for running safety
"""

import os
import subprocess
import sys
import tarfile
from pathlib import Path

import requests

HERE = Path(__file__)
ROOT = HERE.parent.parent
ATEST_OUT = ROOT / "atest" / "output"
IGNORE_IDS = os.environ.get("SAFETY_IGNORE_IDS", "").strip().split()
SAFEY_DB_URL = os.environ["SAFETY_DB_URL"]
SAFETY_PATH = ROOT / ".cache" / "safety-db"
SAFETY_TARBALL = SAFETY_PATH / "safety-db.tar.gz"


def fetch_db():
    if not SAFETY_TARBALL.exists():
        SAFETY_PATH.mkdir(parents=True, exist_ok=True)
        r = requests.get(SAFEY_DB_URL)
        SAFETY_TARBALL.write_bytes(r.content)
        tf = tarfile.open(SAFETY_TARBALL)
        tf.extractall(SAFETY_PATH)


def safety(req_files):
    req_args = sum([["-r", req] for req in ATEST_OUT.rglob("requirements.txt")], [])
    assert req_args, "no requirements.txt found to audit"
    fetch_db()
    ignores = sum([["--ignore", id_] for id_ in IGNORE_IDS], [])
    args = list(
        map(
            str,
            [
                "safety",
                "check",
                "--db",
                next(SAFETY_PATH.glob("*/data")),
                "--full-report",
                *ignores,
                *req_args,
            ],
        )
    )
    print("safety args\n", " ".join(args))
    return subprocess.check_call(args)


if __name__ == "__main__":
    sys.exit(safety(sys.argv[1:]))
