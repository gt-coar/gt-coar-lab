# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
""" Paths

    These will probably only work with the GTCOARLab distribution
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent

PREFIX = Path(sys.prefix).resolve()
PYTHON_EXE = Path(sys.executable)

GTCOARLAB_PATH = PREFIX / "share" / "jupyter" / "gt-coar-lab"
