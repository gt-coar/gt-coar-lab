# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import os
import sys

import jinja2
import ruamel_yaml
from constructor.conda_interface import cc_platform

from . import meta as M
from . import paths as P
from . import utils as U

environ = dict(os.environ)
environ["CONDARC"] = str(P.CONDARC)

THIS

def build_template():
    """ Build a construct.yaml from the project file, lock file
    """
    U.conda_index(cc_platform)
    tmpl = jinja2.Template(P.INSTALLER_TMPL.read_text())
    # TODO: parametrize prefix
    lock_file = P.LOCKS / M.INSTALLER_VERSION / f"cpu-{cc_platform}.conda.lock"
    urls = [
        line for line in lock_file.read_text().splitlines() if line.startswith("https")
    ]

    context = dict(
        name=M.INSTALLER_NAME,
        version=M.INSTALLER_VERSION,
        build_channel=P.CONDA_DIST_URI,
        channels=U.project_channels(),
        specs=urls + [p.as_uri() for p in M.CONDA_TARBALLS.values()],
    )
    P.CONSTRUCT.write_text(tmpl.render(**context))
    ruamel_yaml.safe_load(P.CONSTRUCT.read_text())
    return 0


def build_conda_lab():
    """ Build the static assets for JupyterLab
    """

    return U._(
        [
            "conda-build",
            *U.channel_args(),
            P.LAB_NAME,
            "--output-folder",
            P.CONDA_DIST.resolve(),
        ],
        cwd=P.RECIPES,
        env=environ,
    )

def build_cache():


def build_installer():
    """ Build an installer from the generated construct.yaml
    """
    P.INSTALLER_DIST.exists() or P.INSTALLER_DIST.mkdir(parents=True)

    return U._(
        [
            "constructor",
            ".",
            "--output-dir",
            P.INSTALLER_DIST.resolve(),
            "--cache-dir",
            os.environ.get("CONSTRUCTOR_CACHE", P.CONSTRUCTOR_CACHE.resolve()),
        ],
        cwd=P.INSTALLER,
        env=environ,
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
    sys.exit(build(sys.argv[1:] or list(M.BUILDERS.keys())))
