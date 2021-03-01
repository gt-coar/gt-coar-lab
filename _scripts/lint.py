# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import sys

from . import paths as P
from . import utils as U

PY_LINTERS = [
    ["isort", "-q", "-rc", *P.LINTERS["py"]],
    ["black", "--quiet", *P.LINTERS["py"]],
    ["flake8", *P.LINTERS["py"]],
]

YAML_LINTERS = [["yamllint", *P.LINTERS["yaml"]]]


RFLINT_RULES = [
    "LineTooLong:200",
    "TooFewKeywordSteps:1",
    "TooFewTestSteps:1",
    "TooManyTestSteps:30",
    "TooManyTestCases:13",
]

RFLINT = sum([["--configure", rule] for rule in RFLINT_RULES], [])

ROBOT_LINTERS = [
    ["python", "-m", "robot.tidy", "--inplace", *P.LINTERS["robot"]],
    ["rflint", *RFLINT, *P.LINTERS["robot"]],
    ["python", "-m", "scripts.atest", "--dryrun"],
]


def lint_py():
    for lint_args in PY_LINTERS:
        lint_rc = U._(lint_args, _quiet=True)
        if lint_rc != U.OK:
            break
    return lint_rc


def lint_yaml():
    for lint_args in YAML_LINTERS:
        lint_rc = U._(lint_args, _quiet=True)
        if lint_rc != U.OK:
            break
    return lint_rc


def lint_robot():
    for lint_args in ROBOT_LINTERS:
        lint_rc = U._(lint_args, _quiet=True)
        if lint_rc != U.OK:
            break
    return lint_rc


def lint_prettier(files=None):
    files = files or P.LINTERS["prettier"]
    if not P.NODE_MODULES.exists():
        U._(["yarn", "--prefer-offline"], _quiet=True)
    return U._(
        ["yarn", "prettier", "--loglevel", "warn", "--write", *files], _quiet=True
    )


def lint_ipynb():
    return U._([sys.executable, "-m", "scripts.nblint", *P.ALL_IPYNB], _quiet=True)


def lint(targets):
    lint_rc = 1
    for target in targets:
        linter = globals().get(f"lint_{target}")
        if not linter:
            print(f"don't know how to lint {target}")
            break
        lint_rc = linter()
        if lint_rc != U.OK:
            break
    return lint_rc


if __name__ == "__main__":
    sys.exit(lint(sys.argv[1:] or ["prettier", "py", "yaml", "ipynb"]))
