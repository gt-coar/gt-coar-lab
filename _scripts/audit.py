# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

""" standalone script for running safety
"""

import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import requests

HERE = Path(__file__).parent
ROOT = HERE.parent
SAFETY_OUT = ROOT / "build" / "audit"
SAFETY_IGNORE_IDS = os.environ.get("SAFETY_IGNORE_IDS", "39525").strip().split()
SAFEY_DB_URL = os.environ.get(
    "SAFETY_DB_URL", "https://github.com/pyupio/safety-db/archive/master.tar.gz"
)
SAFETY_PATH = HERE / ".cache" / "safety-db"
SAFETY_TARBALL = SAFETY_PATH / "safety-db.tar.gz"


# packages that aren't trivially normalized
PIP_TO_CONDA = {
    "antlr4-python3-runtime": "antlr-python-runtime",
    "ruamel-yaml-conda": "ruamel.yaml",
    "torch": "pytorch",
}


def norm_name(pkg_name):
    return pkg_name.strip().lower().replace("_", "-")


def fetch_db():
    if not SAFETY_TARBALL.exists():
        SAFETY_PATH.mkdir(parents=True, exist_ok=True)
        r = requests.get(SAFEY_DB_URL)
        SAFETY_TARBALL.write_bytes(r.content)
        tf = tarfile.open(SAFETY_TARBALL)
        tf.extractall(SAFETY_PATH)


def find_conda_req(pip_req, conda_reqs, logfile):
    pip_name = pip_req.split("@")[0].strip()
    print(f"\n{pip_name}\n > {pip_req}", flush=True)
    mapped_name = norm_name(PIP_TO_CONDA.get(pip_name, pip_name))
    if mapped_name != pip_name:
        print(f" >> {mapped_name}", flush=True)

    for conda_req in conda_reqs:
        pattern = f"/{mapped_name}-(.*?)-"
        matches = re.findall(pattern, norm_name(conda_req))
        if matches:
            print(f" >>> {conda_req}", flush=True)
            return f"{pip_name}=={matches[0]}"

    print(f" >>>> NOT FOUND {pip_name}")

    with logfile.open("a+") as fpt:
        fpt.write_text(json.dumps({"missing_pip_req": pip_req}))


def fix_one_req_file(idx, req_file, tdp, logfile):
    conda_reqs = (req_file.parent / "conda.lock").read_text().splitlines()
    req_out = tdp / f"requirements-{idx}.txt"
    reqs = []

    for req in req_file.read_text().splitlines():
        if "@" in req:
            reqs += [find_conda_req(req, conda_reqs, logfile)]
        else:
            reqs += [req]

    req_out.write_text("\n".join(reqs))


def make_req_args(req_files, tdp, logfile):
    for i, req_file in enumerate(req_files):
        fix_one_req_file(i, req_file, tdp, logfile)
    return sum([["-r", req] for req in tdp.rglob("requirements-*.txt")], [])


def safety(out_dir):
    """validate"""
    out_path = Path(out_dir)
    req_file = out_path / "requirements.txt"
    lockfile = out_path / "conda.lock"
    assert req_file.exists(), "no requirements.txt found to audit"
    assert lockfile.exists(), "no conda.lock found to audit"

    logfile = SAFETY_OUT / f"{out_path.stem}.log"

    fetch_db()
    ignores = sum([["--ignore", id_] for id_ in SAFETY_IGNORE_IDS], [])
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        req_args = make_req_args([req_file], tdp, logfile)
        if logfile.exists():
            print("safety log\n", logfile.read_text().strip())

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
        with logfile.open("a+") as fp:
            safety = subprocess.Popen(args, stdout=fp, stderr=fp)
            safety_rc = safety.wait()
        print(logfile.read_text())
        return safety_rc


if __name__ == "__main__":
    sys.exit(safety(sys.argv[1]))
