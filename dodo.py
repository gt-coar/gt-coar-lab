# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
from scripts import meta as M
from scripts import paths as P
from scripts import utils as U

DOIT_CONFIG = {
    "backend": "sqlite3",
    "verbosity": 2,
    "par_type": "thread",
}


# prepare envs
[globals().update(U.make_prepare_task(env_spec)) for env_spec in M.ENVS_TO_PREPARE]

# linting
[
    globals().update(U.make_lint_task(target, files))
    for target, files in P.LINTERS.items()
]

# building
[
    globals().update(U.make_build_task(target, *files))
    for target, files in M.BUILDERS.items()
]
