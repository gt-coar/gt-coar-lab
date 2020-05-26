import sys

from . import paths as P
from . import utils as U

PY_LINTERS = [
    ["isort", "-rc", *P.ALL_PY],
    ["black", *P.ALL_PY],
    ["flake8", *P.ALL_PY],
]


def lint_py():
    for lint_args in PY_LINTERS:
        lint_rc = U._(lint_args)
        if lint_rc != 0:
            break
    return lint_rc


if __name__ == "__main__":
    sys.exit(lint_py())
