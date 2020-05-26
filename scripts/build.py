# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import sys
from datetime import datetime

import jinja2
import ruamel_yaml
from constructor.conda_interface import cc_platform

from . import paths as P
from . import utils as U

PLATFORMS = ["all", cc_platform]

if not cc_platform.startswith("win-"):
    PLATFORMS += ["unix"]


def template():
    """ Build a construct.yaml from the project file, lock file
    """
    lock = ruamel_yaml.safe_load(P.LOCK.read_text())
    proj = ruamel_yaml.safe_load(P.PROJ.read_text())
    tmpl = jinja2.Template(P.INSTALLER_TMPL.read_text())
    today = datetime.today()
    packages = lock["env_specs"][P.ENV]["packages"]
    context = dict(
        version=f"{today.year}.{today.month}.{today.day}-{U.git_commit()}",
        channels=proj["env_specs"][P.ENV]["channels"],
        specs=sorted(sum([packages.get(p, []) for p in PLATFORMS], [])),
    )
    P.CONSTRUCT.write_text(tmpl.render(**context))
    ruamel_yaml.safe_load(P.CONSTRUCT.read_text())
    return 0


def build():
    """ Build an installer from the generated construct.yaml
    """
    P.DIST.exists() or P.DIST.mkdir()

    return U._(
        [
            "constructor",
            ".",
            "--output-dir",
            P.DIST.resolve(),
            "--cache-dir",
            P.CONSTRUCTOR_CACHE.resolve(),
        ],
        cwd=str(P.INSTALLER),
    )


if __name__ == "__main__":
    sys.exit(template() or build())
