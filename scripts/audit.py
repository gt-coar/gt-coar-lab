# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

""" standalone script for running safety
"""

import pkgutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__)
ATEST_OUT = HERE.parent.parent / "atest" / "output"


def safety(req_files):
    req_args = sum([["-r", req] for req in ATEST_OUT.rglob("requirements.txt")], [])
    assert req_args, "no requirements.txt found to audit"
    loader = pkgutil.get_loader("safety_db")
    db = Path(loader.path).parent
    args = ["safety", "check", "--db", db, "--full-report", *req_args]
    return subprocess.check_call(list(map(str, args)))


if __name__ == "__main__":
    sys.exit(safety(sys.argv[1:]))
