# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import pathlib
import sys

PY = pathlib.Path(sys.executable)
AP = "anaconda-project"
APR = [AP, "run"]

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent

PROJ = ROOT / "anaconda-project.yml"
LOCK = ROOT / "anaconda-project-lock.yml"
DIST = ROOT / "dist"
CACHE = ROOT / ".cache"

PACKAGES = ROOT / "packages"

INSTALLER = ROOT / "installer"
RECIPES = ROOT / "recipes"

CONDA_DIST = DIST / "conda-bld"
CONDA_DIST_URI = CONDA_DIST.as_uri()

INSTALLER_TMPL = INSTALLER / "construct.yaml.j2"
CONSTRUCT = INSTALLER / "construct.yaml"
CONSTRUCTOR_CACHE = CACHE / "constructor"

GITHUB = ROOT / ".github"
CI_SUPPORT = ROOT / ".ci_support"

ENVS = ROOT / "envs"

POSTBUILD = ROOT / "postBuild"
LABEXTENSIONS = ROOT / "labextensions.txt"
DODO = ROOT / "dodo.py"

# linting
ALL_PY = sorted(
    [
        *HERE.rglob("*.py"),
        *RECIPES.rglob("*.py"),
        *PACKAGES.rglob("*.py"),
        POSTBUILD,
        DODO,
    ]
)
ALL_YAML = sorted(
    [
        ROOT / ".yamllint",
        ROOT / ".prettierrc",
        *CI_SUPPORT.glob("*.yml"),
        *GITHUB.rglob("*.yml"),
        *ROOT.glob("*.yml"),
        *RECIPES.rglob("*.yaml"),
    ]
)
ALL_MD = sorted([*ROOT.glob("*.md"), *PACKAGES.rglob("*.md")])
ALL_PRETTIER = sorted([*ALL_YAML, *ALL_MD])

LINTERS = dict(prettier=ALL_PRETTIER, py=ALL_PY, yaml=ALL_YAML,)
