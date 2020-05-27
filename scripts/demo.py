import sys

from . import meta as M
from . import paths as P
from . import utils as U


def demo():
    channels = U.channel_args([P.CONDA_DIST_URI])
    U._(["conda", "uninstall", *channels, "gt-coar-lab"])
    U._(["conda", "install", *channels, "--force", M.BUILDERS["conda_lab"][1][0]])
    return 0


if __name__ == "__main__":
    sys.exit(demo())
