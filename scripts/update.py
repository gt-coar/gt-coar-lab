# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import sys
import os
from pathlib import Path

from anaconda_project import project_ops
from anaconda_project.internal.cli.project_load import load_project
from anaconda_project.internal.default_conda_manager import DefaultCondaManager

from . import meta as M
from . import paths as P
from . import utils as U


def _noop_none_(*args, **kwargs):
    return None


def _noop_true_(*args, **kwargs):
    return True


# apply some patches for cross-platform work, without installing
DefaultCondaManager._broken_lock_set_error = _noop_none_
project_ops._try_requirement_without_commit = _noop_true_


def update():
    os.environ["CONDARC"] = str(P.CONDARC)
    proj = load_project(str(Path.cwd()))

    for name, spec in sorted(M.LOCK["env_specs"].items()):
        if spec["locked"]:
            print(
                f"""\n`{name}` will be updated for: {", ".join(spec["platforms"])}\n"""
            )
            project_ops.update(proj, name)

    U._([*P.APR, "lint", "prettier", "yaml"])

    return 0


if __name__ == "__main__":
    sys.exit(update())
