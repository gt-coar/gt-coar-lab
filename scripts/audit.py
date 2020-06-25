# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

""" standalone script for running safety
"""

import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import requests

HERE = Path(__file__)
ROOT = HERE.parent.parent
ATEST_OUT = ROOT / "atest" / "output"
SAFETY_IGNORE_IDS = os.environ.get("SAFETY_IGNORE_IDS", "").strip().split()
SAFEY_DB_URL = os.environ["SAFETY_DB_URL"]
SAFETY_PATH = ROOT / ".cache" / "safety-db"
SAFETY_TARBALL = SAFETY_PATH / "safety-db.tar.gz"

PIP_TO_CONDA = {
    "jupyter-bokeh": "jupyter_bokeh",
    "PyVirtualDisplay": "pyvirtualdisplay",
    "typing-extensions": "typing_extensions",
}


def fetch_db():
    if not SAFETY_TARBALL.exists():
        SAFETY_PATH.mkdir(parents=True, exist_ok=True)
        r = requests.get(SAFEY_DB_URL)
        SAFETY_TARBALL.write_bytes(r.content)
        tf = tarfile.open(SAFETY_TARBALL)
        tf.extractall(SAFETY_PATH)


def find_conda_req(pip_req, conda_reqs):
    pip_name = pip_req.split("@")[0].strip()
    print(f"\n{pip_name}\n > {pip_req}", flush=True)
    mapped_name = PIP_TO_CONDA.get(pip_name, pip_name)
    if mapped_name != pip_name:
        print(f" >> {mapped_name}", flush=True)

    for conda_req in conda_reqs:
        pattern = f"/{mapped_name}-(.*?)-"
        matches = re.findall(pattern, conda_req)
        if matches:
            print(f" >>> {conda_req}", flush=True)
            return f"{pip_name}=={matches[0]}"

    raise Exception(f"could not be resolved pip requirement: {pip_req}")


def fix_one_req_file(idx, req_file, tdp):
    conda_reqs = (req_file.parent / "conda-explicit.txt").read_text().splitlines()
    req_out = tdp / f"requirements-{idx}.txt"
    reqs = []

    for req in req_file.read_text().splitlines():
        if "@" in req:
            reqs += [find_conda_req(req, conda_reqs)]
        else:
            reqs += [req]

    req_out.write_text("\n".join(reqs))


def make_req_args(req_files, tdp):
    for i, req_file in enumerate(req_files):
        fix_one_req_file(i, req_file, tdp)
    return sum([["-r", req] for req in tdp.rglob("requirements-*.txt")], [])


def safety(req_files=None):
    if not req_files:
        req_files = sorted(ATEST_OUT.rglob("requirements.txt"))

    assert req_files, "no requirements.txt found to audit"

    fetch_db()
    ignores = sum([["--ignore", id_] for id_ in SAFETY_IGNORE_IDS], [])
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        req_args = make_req_args(req_files, tdp)
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
        print("safety args\n", " ".join(args), flush=True)
        return subprocess.check_call(args)


if __name__ == "__main__":
    sys.exit(safety(sys.argv[1:]))
