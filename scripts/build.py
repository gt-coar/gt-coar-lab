# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import sys

import jinja2
import ruamel_yaml
from constructor.conda_interface import cc_platform

from . import meta as M
from . import paths as P
from . import utils as U

PLATFORMS = ["all", cc_platform]

if not cc_platform.startswith("win-"):
    PLATFORMS += ["unix"]


def build_template():
    """ Build a construct.yaml from the project file, lock file
    """
    lock = ruamel_yaml.safe_load(P.LOCK.read_text())
    proj = ruamel_yaml.safe_load(P.PROJ.read_text())
    tmpl = jinja2.Template(P.INSTALLER_TMPL.read_text())
    packages = lock["env_specs"][M.INSTALLER_ENV_SPEC]["packages"]
    context = dict(
        name=M.INSTALLER_NAME,
        version=M.VERSION,
        channels=proj["env_specs"][M.INSTALLER_ENV_SPEC]["channels"],
        specs=sorted(sum([packages.get(p, []) for p in PLATFORMS], [])),
    )
    P.CONSTRUCT.write_text(tmpl.render(**context))
    ruamel_yaml.safe_load(P.CONSTRUCT.read_text())
    return 0


def build_installer():
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
        cwd=P.INSTALLER,
    )


def build(targets):
    build_rc = 1
    for target in targets:
        builder = globals().get(f"build_{target}")
        if not builder:
            print(f"don't know how to build {target}")
            break
        build_rc = builder()
        if build_rc != 0:
            break
    return build_rc


if __name__ == "__main__":
    sys.exit(build(sys.argv[1:] or ["template", "installer"]))
