# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

# Derived from https://github.com/krassowski/jupyterlab-lsp/blob/master/scripts/atest.py
# Copyright (c) 2019, jupyter-lsp contributors
# Distributed under the terms of the BSD-3-Clause License

""" Run acceptance tests with robot framework
"""

import os
import shutil
import sys
import time

import robot

from . import meta as M
from . import paths as P
from . import utils as U

OS_ARGS = {
    # notebook and ipykernel releases do not yet support python 3.8 on windows
    # ("Windows"): ["--include", "not-supported", "--runemptysuite"]
}


def get_stem(attempt, extra_args):
    stem = "_".join([M.INSTALLER_PLATFORM, str(attempt)]).replace(".", "_").lower()

    if "--dryrun" in extra_args:
        stem = f"dry_run_{stem}"

    return stem


def atest(attempt, extra_args):
    """ perform a single attempt of the acceptance tests
    """
    extra_args += OS_ARGS.get(M.INSTALLER_VERSION, [])

    stem = get_stem(attempt, extra_args)

    if attempt != 1:
        extra_args += ["--loglevel", "TRACE"]
        previous = P.ATEST_OUT / f"{get_stem(attempt - 1, extra_args)}.robot.xml"
        if previous.exists():
            extra_args += ["--rerunfailed", str(previous)]

    out_dir = P.ATEST_OUT / stem

    args = [
        "--name",
        f"{M.INSTALLER_PLATFORM}",
        "--outputdir",
        out_dir,
        "--output",
        P.ATEST_OUT / f"{stem}.robot.xml",
        "--log",
        P.ATEST_OUT / f"{stem}.log.html",
        "--report",
        P.ATEST_OUT / f"{stem}.report.html",
        "--xunit",
        P.ATEST_OUT / f"{stem}.xunit.xml",
        "--variable",
        f"NAME:{M.INSTALLER_NAME}",
        "--variable",
        f"ATTEMPT:{attempt}",
        "--variable",
        f"OS:{M.INSTALLER_PLATFORM}",
        "--variable",
        f"INSTALLER:{P.INSTALLER_DIST / M.INSTALLER_FILENAME}",
        "--variable",
        f"VERSION:{M.INSTALLER_VERSION}",
        "--randomize",
        "all",
        *(extra_args or []),
        P.ATEST,
    ]

    # print("Robot Arguments\n", " ".join(["robot"] + list(map(str, args))))

    os.chdir(P.ATEST)

    if out_dir.exists():
        print("trying to clean out {}".format(out_dir))
        try:
            shutil.rmtree(out_dir)
        except Exception as err:
            print("Error deleting {}, hopefully harmless: {}".format(out_dir, err))

    print(f"Creating {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        robot.run_cli(list(map(str, args)))
        return U.OK
    except SystemExit as err:
        return err.code


def attempt_atest_with_retries(*extra_args):
    """ retry the robot tests a number of times
    """
    attempt = 0
    error_count = -1

    retries = int(os.environ.get("ATEST_RETRIES") or "0")

    while error_count != 0 and attempt <= retries:
        attempt += 1
        print("attempt {} of {}...".format(attempt, retries + 1))
        start_time = time.time()
        error_count = atest(attempt=attempt, extra_args=list(extra_args))
        print(error_count, "errors in", int(time.time() - start_time), "seconds")

    return error_count


if __name__ == "__main__":
    sys.exit(attempt_atest_with_retries(*sys.argv[1:]))
