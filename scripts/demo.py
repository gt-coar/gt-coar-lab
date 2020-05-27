import sys

from . import meta as M
from . import utils as U


def demo():
    U._(["conda", "install", "--force", M.BUILDERS["conda_lab"][1][0]])
    return 0


if __name__ == "__main__":
    sys.exit(demo())
