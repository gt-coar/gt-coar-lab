# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import subprocess


def short_commit():
    return subprocess.check_output(["git", "rev-parse", "--verify", "HEAD"]).decode(
        "utf-8"
    )[:7]
