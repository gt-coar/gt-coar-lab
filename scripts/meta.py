# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import sys
from datetime import datetime

from . import git as G
from . import paths as P

TODAY = datetime.today()

QA_ENV_SPEC = "qa"
BUILD_ENV_SPEC = "build"

# TODO: something more predictable?
VERSION = f"{TODAY.year}.{TODAY.month}.{TODAY.day}-{G.short_commit()}"

INSTALLER_ENV_SPEC = "gt-coar-lab"
INSTALLER_NAME = "GTCOARLab"

ENVS_TO_PREPARE = [QA_ENV_SPEC, BUILD_ENV_SPEC]

# building
LAB_VERSION = "2.1.3"
LAB_BUILD = "0"

INSTALLER_PLATFORM = {
    "linux": "Linux-x86_64",
    "darwin": "MacOSX-x86_64",
    "win32": "Windows-x86_64",
}[sys.platform]

INSTALLER_EXT = {"win32": "exe", "darwin": "sh", "linux": "sh"}[sys.platform]

INSTALLER_FILENAME = f"{INSTALLER_NAME}-{VERSION}-{INSTALLER_PLATFORM}.{INSTALLER_EXT}"

BUILDERS = dict(
    template=[[P.LOCK, P.INSTALLER_TMPL], [P.CONSTRUCT]],
    conda_lab=[
        [
            P.RECIPES / "gt-coar-lab" / "meta.yaml",
            P.LABEXTENSIONS,
            *((P.PACKAGES / "gt-coar-lab").rglob("*.py")),
        ],
        [P.CONDA_DIST / "noarch" / f"gt-coar-lab-{LAB_VERSION}-py_{LAB_BUILD}.tar.bz2"],
    ],
    installer=[[P.CONSTRUCT], [P.DIST / INSTALLER_FILENAME]],
)

EXTRA_SPECS = [f"gt-coar-lab={LAB_VERSION}=py_{LAB_BUILD}"]
