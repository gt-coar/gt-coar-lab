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
INSTALLER_PLATFORM = {
    "linux": "Linux-x86_64",
    "darwin": "MacOSX-x86_64",
    "win32": "Windows-x86_64",
}[sys.platform]

INSTALLER_EXT = {"win32": "exe", "darwin": "sh", "linux": "sh"}[sys.platform]

INSTALLER_FILENAME = f"{INSTALLER_NAME}-{VERSION}-{INSTALLER_PLATFORM}.{INSTALLER_EXT}"

# GTCOARLab-2020.5.27-89d82c0-MacOSX-x86_64.sh

BUILDERS = dict(
    template=[[P.LOCK, P.INSTALLER_TMPL], [P.CONSTRUCT]],
    installer=[[P.CONSTRUCT], [P.DIST / INSTALLER_FILENAME]],
)
