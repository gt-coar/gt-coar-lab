# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
from doit.tools import config_changed
from scripts import meta as M
from scripts import paths as P
from scripts import utils as U

DOIT_CONFIG = {
    "backend": "sqlite3",
    "verbosity": 2,
    "par_type": "thread",
    "default_tasks": ["ALL"],
}

# locking
def task_lock():
    for prefix, platforms in P.CONDA_LOCK_SRC.items():
        for platform, file_dep in platforms.items():
            yield dict(
                name=f"{prefix}:{platform}",
                file_dep=[*file_dep, P.OK.LINT.prettier],
                targets=[M.CONDA_LOCK_FILES[(prefix, platform)]],
                actions=[
                    [
                        *P.APR,
                        "lock",
                        "--output-folder",
                        P.LOCKS / M.INSTALLER_VERSION,
                        "--platform",
                        platform,
                        "--prefix",
                        f"{prefix}-",
                        "--file",
                        *file_dep,
                    ]
                ],
            )


# phonies
def task_ALL():
    """ do all the normal business
    """
    return dict(file_dep=[P.OK.audit], actions=[["echo", "ALL DONE"]])


# prepare envs
[globals().update(U.make_prepare_task(env_spec)) for env_spec in M.ENVS_TO_PREPARE]

# linting
[
    globals().update(U.make_lint_task(target, files))
    for target, files in P.LINTERS.items()
]


def task_integrity():
    """ ensure the repo is internally consistent
    """
    return dict(
        file_dep=sorted([*P.ALL_PRETTIER, *P.ALL_PY, P.PROJ, U.env_canary("qa")]),
        targets=[P.OK.integrity],
        actions=U._ok(P.OK.integrity, [[*P.APR, "integrity"]]),
    )


# testing
def task_atest():
    """ run acceptance tests
    """
    return dict(
        file_dep=sorted(
            [
                *P.ALL_ROBOT,
                *P.ROBOT_PY,
                P.INSTALLER_DIST / M.INSTALLER_FILENAME,
                P.SCRIPTS / "atest.py",
            ]
        ),
        actions=[[*P.APR, "atest"]],
        task_dep=["lint_robot"],
        targets=[*M.INSTALLED_REQS],
    )


# building
[
    globals().update(U.make_build_task(target, *files))
    for target, files in M.BUILDERS.items()
]


# binding
def task_binder():
    """ ensure the binder requirements are up-to-date
    """
    lock = M.CONDA_LOCK_FILES["cpu", "linux-64"]
    return dict(
        file_dep=[lock],
        actions=[lambda x: P.BINDER_LOCK.write_text(lock.read_text())],
        targets=[P.BINDER_LOCK],
    )


# auditing
def task_audit():
    """ ensure as-installed python requirements are free of _known_ vulnerabilities
    """
    return dict(
        uptodate=[config_changed(dict(ignores=M.SAFETY_IGNORE_IDS))],
        file_dep=[*M.INSTALLED_REQS, P.SCRIPTS / "audit.py"],
        actions=U._ok(P.OK.audit, [[*P.APR, "audit"]]),
        targets=[P.OK.audit],
    )
