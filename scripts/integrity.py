# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import pathlib
import re
import sys
import tempfile

import pytest

from . import meta as M
from . import paths as P

PYTEST_INI = """
[pytest]
junit_family = xunit2
addopts =
    --junitxml dist/xunit/integrity.xunit.xml
"""

LAB_VERSIONS = {
    P.LAB_PACKAGE / "src" / P.LAB_MODULE / "_version.py": r"""__version__ = "(.*?)\"""",
    P.RECIPES / P.LAB_NAME / "meta.yaml": r"""{% set version = "(.*?)" %}""",
    P.LAB_PACKAGE / "setup.cfg": r"version = (.*)",
    P.PROJ: r"- jupyterlab ==(.*)",
    P.BINDER / "environment.yml": r"- jupyterlab ==(.*)",
}


def test_integrity_lab_versions():
    """ all lab versions agree with the TRUTH
    """
    versions = {
        path: re.findall(pattern, path.read_text())
        for path, pattern in LAB_VERSIONS.items()
    }
    for path, found_versions in versions.items():
        assert M.LAB_VERSION in found_versions, path


@pytest.mark.parametrize(
    "the_file,the_path",
    [[path.name, path] for path in [*P.ALL_PY, *P.ALL_MD, *P.ALL_YAML]],
)
def test_integrity_headers(the_file, the_path):
    the_text = the_path.read_text()
    assert M.COPYRIGHT_HEADER in the_text
    assert M.LICENSE_HEADER in the_text


def check_integrity():
    """ actually run the tests
    """
    args = [__file__]

    with tempfile.TemporaryDirectory() as tmp:
        ini = pathlib.Path(tmp) / "pytest.ini"
        ini.write_text(PYTEST_INI)

        args += ["-c", str(ini)]

        return pytest.main(args)


if __name__ == "__main__":
    sys.exit(check_integrity())
