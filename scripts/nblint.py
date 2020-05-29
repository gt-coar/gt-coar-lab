# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import subprocess
import sys
from pathlib import Path

import black
import isort
import nbformat

from . import paths as P


def blacken(source):
    return black.format_str(source, mode=black.FileMode(line_length=88))


def nblint(files):
    for nb_path in map(Path, files):
        nb_text = nb_path.read_text()
        nb_node = nbformat.reads(nb_text, 4)
        changes = 0
        has_empty = 0
        for cell in nb_node.cells:
            cell_type = cell["cell_type"]
            source = "".join(cell["source"])
            if not source.strip():
                has_empty += 1
            if cell_type == "markdown":
                prettier = subprocess.Popen(
                    [
                        P.NODE,
                        P.NODE_MODULES / ".bin" / "prettier",
                        "--stdin-filepath",
                        "foo.md",
                        "--prose-wrap",
                        "always",
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
                out, err = prettier.communicate(source.encode("utf-8"))
                new = out.decode("utf-8").rstrip()
                if new != source:
                    cell["source"] = new.splitlines(True)
                    changes += 1
            elif cell_type == "code":
                if cell["outputs"] or cell["execution_count"]:
                    cell["outputs"] = []
                    cell["execution_count"] = None
                    changes += 1
                if source.startswith("%"):
                    continue
                new = isort.SortImports(file_contents=source).output
                new = blacken(new).rstrip()
                if new != source:
                    cell["source"] = new.splitlines(True)
                    changes += 1

        if has_empty:
            changes += 1
            nb_node.cells = [
                cell for cell in nb_node.cells if "".join(cell["source"]).strip()
            ]

        if changes:
            with nb_path.open("w") as fpt:
                nbformat.write(nb_node, fpt)
            print(nb_path, changes, "changes", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(nblint(sys.argv[1:]))
