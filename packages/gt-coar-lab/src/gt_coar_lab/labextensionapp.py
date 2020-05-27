# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import sys

from jupyterlab import labapp, labextensions

from . import patch_app_dir, patch_build_dir


def main():
    patch_app_dir(labextensions.BaseExtensionApp)
    patch_build_dir(labapp.LabBuildApp)
    return labextensions.main()


if __name__ == "__main__":
    sys.exit(main())
