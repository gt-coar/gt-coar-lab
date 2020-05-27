# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import os
import shutil
import subprocess
import sys
from pathlib import Path

from gt_coar_lab.paths import GTCOARLAB_PATH

SRC_DIR = Path(os.environ["SRC_DIR"])

LABEXTENSIONS = sorted(
    [
        ext.strip()
        for ext in (SRC_DIR / "labextensions.txt").read_text().strip().splitlines()
        if ext.strip() and not ext.startswith("#")
    ]
)


def _(args, **kwargs):
    """ a little wrapper to handle Paths for windows, and echoing
    """
    str_args = [str(a) for a in args]

    print("\n{}\n".format(" ".join(str_args)))

    if "cwd" in kwargs:
        kwargs["cwd"] = str(kwargs["cwd"])

    return subprocess.check_call(str_args, **kwargs)


def build():
    _(["gt-coar-labextension", "install", "--debug", "--no-build", *LABEXTENSIONS])
    _(
        ["gt-coar-lab", "build", "--debug", "--dev-build=False", "--minimize=True",]
    )
    return 0


def clean():
    before = len([*GTCOARLAB_PATH.rglob("*")])

    print("found", before, "files")

    for path in [
        GTCOARLAB_PATH / "staging" / "node_modules",
        GTCOARLAB_PATH / "staging" / "build",
    ]:
        shutil.rmtree(path)

    after_files = sorted(GTCOARLAB_PATH.rglob("*"))
    after = len(after_files)

    print("cleaned", before - after, "files")
    print("will package", after, "files")
    return 0


if __name__ == "__main__":
    sys.exit(build() or clean())
