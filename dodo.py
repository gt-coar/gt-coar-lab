""" automation scripts for building gt-coar-lab

Roughly, the intent is:
- on a contributor's machine
  - derive conda-lock files from yml files
  - derive constructor files from lock file
  - update CI configuration from constructs
- in CI, or a contributor's machine
  - validate well-formedness of the source files
  - build any novel conda packages
  - build an installer
  - test the installer
  - gather test reports
  - combine test reports
  - generate documentation
  - build a release candidate
"""

# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import os
from pathlib import Path

from doit import tools
from ruamel_yaml import safe_load

# see additional environment variable hacks at the end
DOIT_CONFIG = {
    "backend": "sqlite3",
    "verbosity": 2,
    "par_type": "thread",
    "default_tasks": ["ALL"],
}

# patch environment for all child tasks
os.environ.update(
    PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", MAMBA_NO_BANNER="1"
)


def task_setup():
    """handle non-conda setup tasks"""
    yield dict(
        name="yarn",
        doc="install npm dependencies with yarn",
        file_dep=[P.YARN_LOCK, P.PACKAGE_JSON, P.YARNRC],
        actions=[
            tools.CmdAction([*C.YARN], cwd=P.SCRIPTS)
        ],
        targets=[P.YARN_INTEGRITY],
    )


def task_lint():
    """ensure all files match expected style"""
    yield dict(
        name="prettier",
        doc="format YAML, markdown, JSON, etc.",
        file_dep=[*P.ALL_PRETTIER, P.YARN_INTEGRITY],
        actions=[[*C.YARN, "prettier", "--list-different", "--write", *P.ALL_PRETTIER]],
    )

    yield dict(
        name="black",
        doc="format python source",
        file_dep=[*P.ALL_PY, P.PYPROJECT],
        actions=[["isort", *P.ALL_PY], ["black", "--quiet", *P.ALL_PY]],
    )

    yield dict(
        name="yamllint",
        doc="check yaml format",
        task_dep=["lint:prettier"],
        file_dep=[*P.ALL_YAML],
        actions=[["yamllint", *P.ALL_YAML]],
    )


# some namespaces for project-level stuff
class C:
    """constants"""

    ENC = dict(encoding="utf-8")
    YARN = ["yarn", "--silent"]


class P:
    """paths"""

    DODO = Path(__file__)
    ROOT = DODO.parent
    SCRIPTS = ROOT / "_scripts"
    CI = ROOT / ".github"

    # checked in
    CONDARC = CI / ".condarc"
    PACKAGE_JSON = SCRIPTS / "package.json"
    YARNRC = SCRIPTS / ".yarnrc"
    PYPROJECT = SCRIPTS / "pyproject.toml"

    # generated, but checked in
    YARN_LOCK = SCRIPTS / "yarn.lock"
    WORKFLOW = CI / "workflows/ci.yml"

    # stuff we don't check in
    BUILD = ROOT / "build"
    DIST = ROOT / "dist"
    NODE_MODULES = ROOT / "node_modules"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"

    # collections of things
    ALL_PY = [DODO]
    ALL_YAML = [
        *ROOT.glob("*.yml"),
        *ROOT.glob("*.yaml"),
    ]
    ALL_MD = [*ROOT.glob("*.md")]
    ALL_PRETTIER = [
        *ALL_YAML,
        *ALL_MD,
        *ROOT.glob("*.json"),
        CONDARC,
        PYPROJECT,
    ]


class D:
    """data"""

    WORKFLOW = safe_load(P.WORKFLOW.read_text(**C.ENC))


# late environment patches
os.environ.update(
    CONDARC=str(P.CONDARC)
)
