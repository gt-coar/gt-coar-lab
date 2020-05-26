# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import sys

from . import paths as P
from . import utils as U

PY_LINTERS = [
    ["isort", "-rc", *P.ALL_PY],
    ["black", *P.ALL_PY],
    ["flake8", *P.ALL_PY],
]

YAML_LINTERS = [["yamllint", *P.ALL_YAML]]


def lint_py():
    for lint_args in PY_LINTERS:
        lint_rc = U._(lint_args)
        if lint_rc != 0:
            break
    return lint_rc


def lint_yaml():
    for lint_args in YAML_LINTERS:
        lint_rc = U._(lint_args)
        if lint_rc != 0:
            break
    return lint_rc


if __name__ == "__main__":
    sys.exit(lint_py() or lint_yaml())
