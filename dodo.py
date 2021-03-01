""" automation scripts for building gt-coar-lab

Roughly, the intent is:
- on a contributor's machine
  - derive conda-lock files from yml files
  - derive constructor files from lock file
  - update CI configuration from constructs
- in CI, or a contributor's machine
  - validate well-formedness of the source files
  - build any novel conda packages
  - build an installer
  - test the installer
  - gather test reports
  - combine test reports
  - generate documentation
  - build a release candidate
"""

# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
import os
from datetime import datetime
from pathlib import Path

from doit.tools import CmdAction, create_folder
from jinja2 import Template
from ruamel_yaml import safe_load

# see additional environment variable hacks at the end
DOIT_CONFIG = {"backend": "sqlite3", "verbosity": 2, "par_type": "thread"}

# patch environment for all child tasks
os.environ.update(
    MAMBA_NO_BANNER="1",
    CONDA_EXE="mamba",
)


def task_setup():
    """handle non-conda setup tasks"""

    yarn_dep = [P.PACKAGE_JSON, P.YARNRC]

    if P.YARN_LOCK.exists():
        yarn_dep += [P.YARN_LOCK]

    yield dict(
        name="yarn",
        doc="install npm dependencies with yarn",
        file_dep=yarn_dep,
        actions=[U.script(C.YARN)],
        targets=[P.YARN_INTEGRITY],
    )


def task_lint():
    """ensure all files match expected style"""
    yield dict(
        name="prettier",
        doc="format YAML, markdown, JSON, etc.",
        file_dep=[*P.ALL_PRETTIER, P.YARN_INTEGRITY, P.PRETTIERRC],
        actions=[
            U.script(
                [
                    *P.PRETTIER_ARGS,
                    *P.ALL_PRETTIER,
                ]
            )
        ],
    )

    yield dict(
        name="black",
        doc="format python source",
        file_dep=[*P.ALL_PY, P.PYPROJECT],
        actions=[
            U.script(["isort", *P.ALL_PY]),
            U.script(["black", "--quiet", *P.ALL_PY]),
        ],
    )

    yield dict(
        name="yamllint",
        doc="check yaml format",
        task_dep=["lint:prettier"],
        file_dep=[*P.ALL_YAML],
        actions=[U.script(["yamllint", *P.ALL_YAML])],
    )


def task_lock():
    """generate conda locks for all envs"""
    for variant in C.VARIANTS:
        for subdir in C.SUBDIRS:
            variant_spec = U.variant_spec(variant, subdir)
            if variant_spec is None:
                continue
            args = ["conda-lock", "--mamba", "--platform", subdir]
            lockfile = P.LOCKS / f"{variant}-{subdir}.conda.lock"
            specs = [*P.CORE_SPECS, P.SPECS / f"{subdir}.yml", variant_spec]
            args += sum([["--file", spec] for spec in specs], [])
            args += ["--filename-template", variant + "-{platform}.conda.lock"]

            yield dict(
                name=f"{variant}:{subdir}",
                file_dep=specs,
                actions=[
                    (create_folder, [P.LOCKS]),
                    U.cmd(args, cwd=str(P.LOCKS)),
                ],
                targets=[lockfile],
            )

    for subdir in C.SUBDIRS:
        args = ["conda-lock", "--mamba", "--platform", subdir]
        lockfile = P.LOCKS / f"ci-{subdir}.conda.lock"
        specs = [P.SPECS / "ci.yml"]
        args += sum([["--file", spec] for spec in specs], [])
        args += ["--filename-template", "ci-{platform}.conda.lock"]
        yield dict(
            name=f"ci:{subdir}",
            file_dep=specs,
            actions=[
                (create_folder, [P.LOCKS]),
                U.cmd(args, cwd=str(P.LOCKS)),
            ],
            targets=[lockfile],
        )


def task_construct():
    """generate construct folders"""
    for variant in C.VARIANTS:
        for subdir in C.SUBDIRS:
            if U.variant_spec(variant, subdir) is not None:
                yield U.construct(variant, subdir)


def task_ci():
    """generate CI workflows"""
    tmpl = P.TEMPLATES / "workflows/ci.yml.j2"

    def build():
        P.WORKFLOW.write_text(Template(tmpl.read_text(**C.ENC)).render({}), **C.ENC)
        U.script([*P.PRETTIER_ARGS, P.WORKFLOW]).execute()

    yield dict(
        name="workflow",
        actions=[build],
        file_dep=[tmpl, P.YARN_INTEGRITY],
        targets=[P.WORKFLOW],
    )


def task_build():
    """build installers"""
    for variant in C.VARIANTS:
        for subdir in C.SUBDIRS:
            if U.variant_spec(variant, subdir) is not None:
                yield U.build(variant, subdir)


# some namespaces for project-level stuff
class C:
    """constants"""

    NAME = "GTCoarLab"
    ENC = dict(encoding="utf-8")
    YARN = ["yarn", "--silent"]
    VARIANTS = ["cpu", "gpu"]
    SUBDIRS = ["linux-64", "osx-64", "win-64"]
    TODAY = datetime.today()
    VERSION = TODAY.strftime("%Y.%m")
    BUILD_NUMBER = "0"
    CONSTRUCTOR_PLATFORM = {
        "linux-64": ["Linux-x86_64", "sh"],
        "osx-64": ["MacOSX-x86_64", "sh"],
        "win-64": ["Windows-x86_64", "exe"],
    }


class P:
    """paths"""

    DODO = Path(__file__)
    ROOT = DODO.parent
    SCRIPTS = ROOT / "_scripts"
    CI = ROOT / ".github"

    # checked in
    CONDARC = CI / ".condarc"
    PACKAGE_JSON = SCRIPTS / "package.json"
    YARNRC = SCRIPTS / ".yarnrc"
    PYPROJECT = SCRIPTS / "pyproject.toml"
    TEMPLATES = ROOT / "templates"
    SPECS = ROOT / "specs"
    CACHE = SCRIPTS / ".cache"
    CONSTRUCTOR_CACHE = Path(
        os.environ.get("CONSTRUCTOR_CACHE", CACHE / ".constructor")
    )

    # generated, but checked in
    YARN_LOCK = SCRIPTS / "yarn.lock"
    WORKFLOW = CI / "workflows/ci.yml"
    LOCKS = ROOT / "locks"
    CONSTRUCTS = ROOT / "constructs"

    # stuff we don't check in
    BUILD = ROOT / "build"
    DIST = ROOT / "dist"
    NODE_MODULES = SCRIPTS / "node_modules"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"

    # config cruft
    PRETTIER_SUFFIXES = [".yml", ".yaml", ".toml", ".json", ".md"]
    PRETTIERRC = SCRIPTS / ".prettierrc"
    PRETTIER_ARGS = [
        *C.YARN,
        "prettier",
        "--config",
        PRETTIERRC,
        "--list-different",
        "--write",
    ]

    # collections of things
    CORE_SPECS = [SPECS / "_base.yml", SPECS / "core.yml"]
    ALL_PY = [DODO]
    ALL_YAML = [
        *SPECS.glob("*.yml"),
        *CI.rglob("*.yml"),
    ]
    ALL_MD = [*ROOT.glob("*.md")]
    ALL_PRETTIER = [
        *ALL_YAML,
        *ALL_MD,
        *SCRIPTS.glob("*.json"),
        *CI.glob("*.yml"),
        CONDARC,
    ]


class U:
    """utilities"""

    cmd = lambda *args, **kwargs: CmdAction(*args, **kwargs, shell=False)
    script = lambda *args, **kwargs: U.cmd(*args, **kwargs, cwd=str(P.SCRIPTS))

    @classmethod
    def variant_spec(cls, variant, subdir):
        spec = P.SPECS / f"{variant}-{subdir}.yml"
        return spec if spec.exists() else None

    @classmethod
    def installer(cls, variant, subdir):
        pf, ext = C.CONSTRUCTOR_PLATFORM[subdir]
        name = f"{C.NAME}-{variant.upper()}-{C.VERSION}-{C.BUILD_NUMBER}-{pf}.{ext}"
        return P.DIST / name

    @classmethod
    def construct(cls, variant, subdir):
        construct = P.CONSTRUCTS / f"{variant}-{subdir}"
        lock = P.LOCKS / f"{variant}-{subdir}.conda.lock"
        tmpl_dir = P.TEMPLATES / "construct"
        templates = tmpl_dir.rglob("*")
        paths = {
            t: construct / (str(t.relative_to(tmpl_dir)).replace(".j2", ""))
            for t in templates
        }
        context = dict(
            specs=lock.read_text(**C.ENC).split("@EXPLICIT")[1].strip().splitlines(),
            name=C.NAME,
            variant=variant,
            build_number=C.BUILD_NUMBER,
            version=C.VERSION,
        )

        def construct():
            for src_path, dest_path in paths.items():
                if not dest_path.parent.exists():
                    dest_path.parent.mkdir(parents=True)
                src = src_path.read_text(**C.ENC)
                if src_path.name.endswith(".j2"):
                    dest = Template(src).render(**context)
                else:
                    dest = src
                dest_path.write_text(dest, **C.ENC)
                if dest_path.suffix in P.PRETTIER_SUFFIXES:
                    U.script([*P.PRETTIER_ARGS, dest_path]).execute()

        yield dict(
            name=f"{variant}:{subdir}",
            actions=[construct],
            file_dep=[lock, *paths.keys()],
            targets=[*paths.values()],
        )

    @classmethod
    def build(cls, variant, subdir):
        construct = P.CONSTRUCTS / f"{variant}-{subdir}"
        yield dict(
            name=f"{variant}:{subdir}",
            actions=[
                U.cmd(
                    [
                        "constructor",
                        ".",
                        "--output-dir",
                        P.DIST,
                        "--cache-dir",
                        P.CONSTRUCTOR_CACHE,
                    ],
                    cwd=str(construct),
                )
            ],
            file_dep=[*construct.rglob("*")],
            targets=[U.installer(variant, subdir)],
        )


# late environment patches
os.environ.update(CONDARC=str(P.CONDARC))
