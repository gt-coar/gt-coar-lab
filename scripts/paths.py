# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import pathlib
import shutil
import sys

PY = pathlib.Path(sys.executable)
AP = "anaconda-project"
APR = [AP, "run"]
NODE = shutil.which("node") or shutil.which("node.cmd") or shutil.which("node.exe")

SCRIPTS = pathlib.Path(__file__).parent
ROOT = SCRIPTS.parent

# files
DODO = ROOT / "dodo.py"
LOCK = ROOT / "anaconda-project-lock.yml"
PROJ = ROOT / "anaconda-project.yml"

# folders
BINDER = ROOT / "binder"
CACHE = ROOT / ".cache"
CI_SUPPORT = ROOT / ".ci_support"
DIST = ROOT / "dist"
ENVS = ROOT / "envs"
GITHUB = ROOT / ".github"
INSTALLER = ROOT / "installer"
NODE_MODULES = ROOT / "node_modules"
NOTEBOOKS = ROOT / "notebooks"
PACKAGES = ROOT / "packages"
RECIPES = ROOT / "recipes"
ATEST = ROOT / "atest"
ATEST_LIBS = ATEST / "libraries"

LAB_NAME = "gt-coar-lab"
LAB_MODULE = LAB_NAME.replace("-", "_")
LAB_PACKAGE = PACKAGES / LAB_NAME


CONDA_DIST = DIST / "conda-bld"
CONDA_DIST_URI = CONDA_DIST.as_uri()

INSTALLER_DIST = DIST / "installers"

INSTALLER_TMPL = INSTALLER / "construct.yaml.j2"
CONSTRUCT = INSTALLER / "construct.yaml"
CONSTRUCTOR_CACHE = CACHE / "constructor"

# testing
ATEST_OUT = ATEST / "output"

# demoing
BINDER_ENV = BINDER / "environment.yml"
POSTBUILD = BINDER / "postBuild"
LABEXTENSIONS = BINDER / "labextensions.txt"

# linting
ROBOT_PY = sorted((ATEST_LIBS).rglob("*.py"))
ALL_PY = sorted(
    [
        *ROBOT_PY,
        *SCRIPTS.rglob("*.py"),
        *PACKAGES.rglob("*.py"),
        *RECIPES.rglob("*.py"),
        POSTBUILD,
        DODO,
    ]
)
ALL_YAML = sorted(
    [
        ROOT / ".yamllint",
        ROOT / ".prettierrc",
        BINDER_ENV,
        *CI_SUPPORT.glob("*.yml"),
        *GITHUB.rglob("*.yml"),
        *ROOT.glob("*.yml"),
        *RECIPES.rglob("*.yaml"),
    ]
)
ALL_MD = sorted([*ROOT.glob("*.md"), *PACKAGES.rglob("*.md")])
ALL_PRETTIER = sorted([*ALL_YAML, *ALL_MD])
ALL_IPYNB = [
    ipynb
    for ipynb in sorted(NOTEBOOKS.rglob("*.ipynb"))
    if ".ipynb_checkpoints" not in str(ipynb)
]
ALL_ROBOT = sorted(ATEST.rglob("*.robot"))

LINTERS = dict(
    prettier=ALL_PRETTIER, py=ALL_PY, yaml=ALL_YAML, ipynb=ALL_IPYNB, robot=ALL_ROBOT
)

# logging
BUILD = ROOT / "build"

# simple ouputs for less-deterministic processes
class OK:
    audit = BUILD / "audit.ok"
    integrity = BUILD / "integrity.ok"
