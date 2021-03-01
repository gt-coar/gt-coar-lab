# Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

import os
import shutil
import sys
import tempfile
from argparse import ArgumentParser
from pathlib import Path

from conda.models.match_spec import MatchSpec
from ruamel_yaml import safe_dump, safe_load

from . import paths as P
from . import utils as U


def make_parser() -> ArgumentParser:
    parser = ArgumentParser(description="conda-pack from multiple env files")
    parser.add_argument(
        "--file",
        dest="env_files",
        metavar="FILE",
        nargs="+",
        help="a conda environment YAML file",
    )
    parser.add_argument("--prefix", help="prefix to add to file")
    parser.add_argument(
        "--platform",
        metavar="PLATFORM",
        nargs="+",
        help="platform to solve",
        dest="platforms",
    )
    parser.add_argument("--output-folder", default=".", help="where to put lock files")
    return parser


def parse_specs(env):
    for dep in env["dependencies"]:
        spec = MatchSpec(dep)
        yield spec.name, dep


def merge(env, composite):
    print(f"""\nmerging {env["name"]}""", flush=True)
    print("> channels", flush=True)
    for channel in env.get("channels", []):
        if channel not in composite["channels"]:
            print("\t+ {channel}")
            composite["channels"] = [channel, *composite["channels"]]

    env_specs, comp_specs = dict(parse_specs(env)), dict(parse_specs(composite))

    print("> dependencies", flush=True)
    for name, dep in env_specs.items():
        if name in comp_specs:
            print(f"""\t- {comp_specs[name]}""", flush=True)
        print(f"""\t+ {dep}""", flush=True)
        comp_specs[name] = dep

    composite["dependencies"] = [*comp_specs.values()]

    return composite


def lock(env_files, platforms, prefix, output_folder):
    output_folder = Path(output_folder).resolve()
    envs = [safe_load(Path(env).read_text(encoding="utf-8")) for env in env_files]

    composite = envs[0]

    for env in envs[1:]:
        composite = merge(env, composite)

    environ = dict(os.environ)
    environ.update(CONDARC=str(P.CONDARC))

    for platform in platforms:
        out = output_folder / f"{prefix}{platform}.conda.lock"
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            env = tdp / f"{prefix}{platform}-environment.yml"
            env.write_text(
                safe_dump(composite, default_flow_style=False), encoding="utf-8"
            )
            U._(
                ["conda-lock", "--platform", platform, "--file", env],
                cwd=tdp,
                env=environ,
            )

            if not out.parent.exists():
                out.parent.mkdir(parents=True)
            lock = tdp / f"conda-{platform}.lock"
            shutil.copy2(lock, out)
    return U.OK


def main(argv=None):
    args = dict(**vars(make_parser().parse_args(argv)))
    return lock(**args)


if __name__ == "__main__":
    sys.exit(main())
