# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import subprocess


def git_commit():
    return subprocess.check_output(["git", "rev-parse", "--verify", "HEAD"]).decode(
        "utf-8"
    )[:7]


def _(args, **kwargs):
    """ a little wrapper to handle Paths for windows, and echoing
    """
    str_args = [str(a) for a in args]

    print("\n{}\n".format(" ".join(str_args)))

    if "cwd" in kwargs:
        kwargs["cwd"] = str(kwargs["cwd"])

    return subprocess.check_call(str_args, **kwargs)
