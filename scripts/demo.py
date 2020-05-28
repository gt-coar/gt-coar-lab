# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import sys

from . import meta as M
from . import paths as P
from . import utils as U


def demo():
    channels = U.channel_args([P.CONDA_DIST_URI])
    try:
        U._(["conda", "uninstall", *channels, P.LAB_NAME])
    except Exception:
        pass
    U._(["conda", "install", *channels, "--force", M.BUILDERS["conda_lab"][1][0]])
    return 0


if __name__ == "__main__":
    sys.exit(demo())
