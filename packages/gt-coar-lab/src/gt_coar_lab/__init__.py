# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import os

from ._version import __version__  # noqa
from .paths import GTCOARLAB_PATH


def patch_app_dir(app_klass):
    path = str(GTCOARLAB_PATH)
    os.environ["JUPYTERLAB_DIR"] = path
    app_klass.app_dir.default_value = path
    return path


def patch_build_dir(build_klass):
    build_klass.name.default_value = "GTCOARLab"
