# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import pathlib

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
INSTALLER = ROOT / "installer"
INSTALLER_TMPL = INSTALLER / "construct.yaml.j2"
CONSTRUCT = INSTALLER / "construct.yaml"
PROJ = ROOT / "anaconda-project.yml"
LOCK = ROOT / "anaconda-project-lock.yml"
DIST = ROOT / "dist"
CACHE = ROOT / ".cache"
CONSTRUCTOR_CACHE = CACHE / "constructor"

GITHUB = ROOT / ".github"
CI_SUPPORT = ROOT / ".ci_support"
ENV = "gt-coar-lab"

ALL_PY = sorted([*HERE.rglob("*.py"), ROOT / "postBuild"])
ALL_YAML = sorted(
    [*HERE.glob("*.yml"), *GITHUB.glob("*.yml"), *CI_SUPPORT.glob("*.yml")]
)
