# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import os
import sys
from datetime import datetime

import yaml

from . import paths as P

PROJ = yaml.safe_load(P.PROJ.read_text())
LOCK = yaml.safe_load(P.LOCK.read_text())

QA_ENV_SPEC = "qa"
BUILD_ENV_SPEC = "build"
BINDER_ENV_SPEC = "_binder"


ENVS_TO_PREPARE = [QA_ENV_SPEC, BUILD_ENV_SPEC]

# building
LAB_VERSION = "2.1.5"
LAB_BUILD = "0"

ALL_PLATFORMS = ["linux", "macosx", "windows"]

INSTALLER_VERSION = os.environ.get(
    "INSTALLER_VERSION", PROJ["variables"]["INSTALLER_VERSION"]
)
INSTALLER_NAME = "GTCOARLab"
INSTALLER_PLATFORM, INSTALLER_EXT = {
    "linux": ["Linux", "sh"],
    "darwin": ["MacOSX", "sh"],
    "win32": ["Windows", "exe"],
}[sys.platform]

INSTALLER_ENV_STEM = P.LAB_NAME
INSTALLER_ENV_SPEC = f"{INSTALLER_ENV_STEM}-{INSTALLER_PLATFORM.lower()}"

INSTALLER_FILENAME = (
    f"{INSTALLER_NAME}-{INSTALLER_VERSION}-{INSTALLER_PLATFORM}-x86_64.{INSTALLER_EXT}"
)
INSTALLED_REQS = P.ATEST_OUT / f"{INSTALLER_PLATFORM.lower()}_1" / "requirements.txt"

CONDA_TARBALLS = {
    P.LAB_NAME: P.CONDA_DIST
    / "noarch"
    / f"{P.LAB_NAME}-{LAB_VERSION}-py_{LAB_BUILD}.tar.bz2"
}

BUILDERS = dict(
    template=[[P.LOCK, P.INSTALLER_TMPL], [P.CONSTRUCT]],
    conda_lab=[
        [
            P.RECIPES / P.LAB_NAME / "meta.yaml",
            P.LABEXTENSIONS,
            *(P.LAB_PACKAGE.rglob("*.py")),
        ],
        [CONDA_TARBALLS[P.LAB_NAME]],
    ],
    installer=[
        [P.CONSTRUCT, CONDA_TARBALLS[P.LAB_NAME]],
        [P.INSTALLER_DIST / INSTALLER_FILENAME],
    ],
)

EXTRA_SPECS = [f"{P.LAB_NAME}={LAB_VERSION}=py_{LAB_BUILD}"]


YEAR = f"{datetime.today().year}"
COPYRIGHT_HEADER = (
    f"{YEAR} University System of Georgia and {INSTALLER_NAME} Contributors"
)
LICENSE_HEADER = "Distributed under the terms of the BSD-3-Clause License"
