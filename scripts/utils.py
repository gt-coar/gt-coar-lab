# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import subprocess

from . import meta as M
from . import paths as P

OK = 0
ERROR = 1


def _(args, _quiet=False, **kwargs):
    """ a little wrapper to handle Paths for windows, and echoing
    """
    str_args = [str(a) for a in args]

    if not _quiet:
        print("\n{}\n".format(" ".join(str_args)))

    if "cwd" in kwargs:
        kwargs["cwd"] = str(kwargs["cwd"])

    return subprocess.call(str_args, **kwargs)


def project_channels():
    return M.PROJ["env_specs"][M.INSTALLER_ENV_SPEC]["channels"]


def channel_args(pre=None, post=None):
    all_channels = [*(pre or []), *project_channels(), *(post or [])]
    return sum([["-c", c] for c in all_channels], [])


def conda_index(ensure_subdir=None):
    if ensure_subdir:
        subdir = P.CONDA_DIST / ensure_subdir
        subdir.mkdir(parents=True, exist_ok=True)

    [[p.chmod(0o777), print(p)] for p in sorted(P.CONDA_DIST.rglob("*"))]

    return _(["conda", "index", P.CONDA_DIST])


# doit stuff
def env_canary(env_spec):
    return P.ENVS / env_spec / "conda-meta" / "history"


def make_prepare_task(env_spec):
    def task():
        return dict(
            file_dep=[P.LOCK],
            targets=[env_canary(env_spec)],
            actions=[[P.AP, "prepare", "--env-spec", env_spec]],
        )

    task.__name__ = f"task_prep_{env_spec}"
    task.__doc__ = f"prepare environment {env_spec}"

    return {task.__name__: task}


def make_lint_task(target, files):
    def task():
        ok = getattr(P.OK.LINT, target)
        return dict(
            file_dep=[*files, env_canary("qa"), P.SCRIPTS / "lint.py",],
            actions=[
                lambda: [ok.unlink() if ok.exists() else None, None][-1],
                [*P.APR, "lint", target],
                lambda: [ok.parent.mkdir(exist_ok=True), ok.touch(), None][-1],
            ],
            targets=[ok],
        )

    task.__name__ = f"task_lint_{target}"
    task.__doc__ = f"lint/format {target}"

    return {task.__name__: task}


def make_build_task(target, file_dep, targets):
    def task():
        return dict(
            file_dep=[*file_dep, env_canary("build")],
            targets=targets,
            actions=[[*P.APR, "build", target]],
        )

    task.__name__ = f"task_build_{target}"
    task.__doc__ = f"build {target}"

    return {task.__name__: task}


def _ok(path, actions):
    """ wrap a task in an sentiinel
    """

    def unok():
        path.exists() and path.unlink()

    def ok():
        if not path.parent.is_dir():
            path.parent.mkdir()
        path.write_text("ok")

    return [unok, *actions, ok]
