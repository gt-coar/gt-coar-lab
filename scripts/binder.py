# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import sys

import yaml

from . import meta as M
from . import paths as P
from .lint import lint_prettier


def binder():
    needs_inheriting = [M.BINDER_ENV_SPEC]
    channels = []
    dependencies = []

    while needs_inheriting:
        env_spec = M.PROJ["env_specs"][needs_inheriting.pop()]
        channels += env_spec.get("channels", [])
        dependencies += env_spec.get("packages", [])
        needs_inheriting += env_spec.get("inherit_from", [])

    P.BINDER_ENV.write_text(
        "# {}\n# {}\n\n{}".format(
            M.COPYRIGHT_HEADER,
            M.LICENSE_HEADER,
            yaml.safe_dump(
                dict(
                    name=P.LAB_NAME,
                    channels=channels,
                    dependencies=sorted(set(dependencies)),
                )
            ),
        )
    )

    return lint_prettier([P.BINDER_ENV])


if __name__ == "__main__":
    sys.exit(binder())
