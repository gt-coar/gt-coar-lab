""" automation scripts for building gt-coar-lab

Roughly, the intent is:
- on a contributor's machine
  - [x] derive conda-lock files from yml files
  - [x] derive constructor files from lock file
  - [x] update CI configuration from constructs
- in CI, or a contributor's machine
  - [x] validate well-formedness of the source/generated files
  - [ ] build any novel conda packages
  - [x] build an installer
  - [x] test the installer
  - [x] gather test reports
  - [x] combine test reports
  - [x] audit python packages for known-bad versions
  - [ ] generate documentation
  - [ ] build a release candidate
"""

# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

# see the HACKS at the end of this file for DOIT_CONFIG, env vars, encoding cruft

import json
import logging
import os
import platform
import shutil
import subprocess
from datetime import datetime
from hashlib import sha256
from pathlib import Path

import colorama
from doit.reporter import ConsoleReporter
from doit.tools import CmdAction, create_folder
from jinja2 import Template
from ruamel_yaml import safe_load

# init logging
# TODO: make configurable
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# actual tasks
def task_setup():
    """handle non-conda setup tasks"""

    yarn_dep = [P.PACKAGE_JSON, P.YARNRC]

    if P.YARN_LOCK.exists():
        yarn_dep += [P.YARN_LOCK]

    yield dict(
        name="yarn",
        doc="install npm dependencies with yarn",
        file_dep=yarn_dep,
        actions=[U.script(P.YARN)],
        targets=[P.YARN_INTEGRITY],
    )


def task_lint():
    """ensure all files match expected style"""
    if C.SKIP_LINT:
        return

    yield dict(
        name="prettier",
        doc="format YAML, markdown, JSON, etc.",
        file_dep=[*P.ALL_PRETTIER, P.YARN_INTEGRITY, P.PRETTIERRC],
        actions=[
            U.script(
                [
                    *P.PRETTIER,
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
            U.script(["flake8", "--max-line-length=88", "--ignore=E731", *P.ALL_PY]),
        ],
    )

    yield dict(
        name="yamllint",
        doc="check yaml format",
        task_dep=["lint:prettier"],
        file_dep=[*P.ALL_YAML],
        actions=[U.script(["yamllint", *P.ALL_YAML])],
    )

    yield dict(
        name="robot",
        doc="format and lint robot",
        file_dep=[*P.ALL_ROBOT],
        actions=[
            ["python", "-m", "robot.tidy", "-r", P.ATEST],
            ["python", "-m", "rflint", *P.ALL_ROBOT],
        ],
    )

    yield dict(
        name="shell",
        doc="format and lint shell scripts",
        file_dep=[*P.ALL_SH],
        actions=[["beautysh", *P.ALL_SH], ["shellcheck", *P.ALL_SH]],
    )

    for path in P.ALL_HEADER_FILES:
        yield dict(
            name=f"headers:{path.relative_to(P.ROOT)}",
            file_dep=[path],
            actions=[(U.headers, [path])],
        )

    yield dict(
        name="changelog",
        doc="ensure changelog is good",
        file_dep=[P.VERSION, P.CHANGELOG],
        actions=[
            lambda: f"## {P.VERSION.read_text(**C.ENC).strip()}"
            in P.CHANGELOG.read_text(**C.ENC)
        ],
    )


def task_lock():
    """generate conda locks for all envs"""
    if C.SKIP_LOCKS:
        return

    for subdir in C.SUBDIRS:
        yield U.lock("atest", None, subdir)
        yield U.lock("audit", None, subdir, include_base=False)
        yield U.lock("build", None, subdir)
        yield U.lock("dev", None, subdir, ["build", "lint", "atest", "audit"])
        yield U.lock("lint", None, subdir)

        for variant in C.VARIANTS:
            variant_spec = U.variant_spec(variant, subdir)
            if variant_spec:
                yield U.lock("run", variant, subdir)

        if subdir == "linux-64":
            yield U.lock("binder", None, subdir, ["run"])


def task_construct():
    """generate construct folders"""
    if C.CI:
        return
    for variant in C.VARIANTS:
        for subdir in C.SUBDIRS:
            if U.variant_spec(variant, subdir) is not None:
                yield U.construct(variant, subdir)


def task_ci():
    """generate CI workflows"""
    if C.CI:
        return
    tmpl = P.TEMPLATES / "workflows/ci.yml.j2"

    context = dict(copyright=C.COPYRIGHT_HEADER, license=C.LICENSE_HEADER, jobs=[])

    for variant in C.VARIANTS:
        for subdir in C.SUBDIRS:
            if U.variant_spec(variant, subdir) is not None:
                context["jobs"] += [
                    dict(
                        subdir=subdir,
                        variant=variant,
                        build_lockfile=str(
                            (P.LOCKS / f"build-{subdir}.conda.lock").relative_to(P.ROOT)
                        ),
                        atest_lockfile=str(
                            (P.LOCKS / f"atest-{subdir}.conda.lock").relative_to(P.ROOT)
                        ),
                        audit_lockfile=str(
                            (P.LOCKS / f"audit-{subdir}.conda.lock").relative_to(P.ROOT)
                        ),
                        vm=C.VM[subdir],
                        installer_name=U.installer(variant, subdir).name,
                        tmp_uri="file:///c:/tmp"
                        if subdir == "win-64"
                        else "file:///tmp",
                    )
                ]

    def build():
        P.WORKFLOW.write_text(
            Template(tmpl.read_text(**C.ENC)).render(**context), **C.ENC
        )

    yield dict(
        name="workflow",
        actions=[build, U.script([*P.PRETTIER, P.WORKFLOW])],
        file_dep=[tmpl, P.YARN_INTEGRITY],
        targets=[P.WORKFLOW],
    )


def task_build():
    """build installers"""
    for subdir in C.SUBDIRS:
        if subdir == C.THIS_SUBDIR:
            for variant in C.VARIANTS:
                if U.variant_spec(variant, subdir) is not None:
                    for task in U.build(variant, subdir):
                        yield task


def task_test():
    """test installers"""
    for variant in C.VARIANTS:
        for subdir in C.SUBDIRS:
            if subdir != C.THIS_SUBDIR:
                continue
            installer = U.installer(variant, subdir)
            hashfile = installer.parent / f"{installer.name}.sha256"
            out_dir = P.ATEST_OUT / f"{variant}-{subdir}-0"
            pip_reqs = out_dir / "requirements.txt"
            lockfile = out_dir / "conda.lock"

            yield dict(
                name=f"{variant}:{subdir}",
                file_dep=[hashfile, installer, *P.ALL_ROBOT],
                actions=[(U.atest, [variant, subdir])],
                targets=[
                    P.ATEST_OUT / f"{variant}-{subdir}-0.robot.xml",
                    pip_reqs,
                    lockfile,
                ],
            )


def task_audit():
    """audit observed pip packages"""
    for variant in C.VARIANTS:
        for subdir in C.SUBDIRS:
            out_dir = P.ATEST_OUT / f"{variant}-{subdir}-0"
            pip_reqs = out_dir / "requirements.txt"
            lockfile = out_dir / "conda.lock"
            yield dict(
                name=f"{variant}:{subdir}",
                file_dep=[pip_reqs, lockfile, P.SCRIPTS / "audit.py"],
                actions=[(create_folder, [P.AUDIT_OUT]), (U.audit, [variant, subdir])],
                targets=[P.AUDIT_OUT / f"{variant}-{subdir}.log"],
            )


# some namespaces for project-level stuff
class P:
    """paths"""

    DODO = Path(__file__)
    ROOT = DODO.parent
    VERSION = ROOT / "VERSION"

    # checked in
    GITHUB = ROOT / ".github"
    TEMPLATES = ROOT / "templates"
    SPECS = ROOT / "specs"
    ATEST = ROOT / "atest"
    BINDER = ROOT / ".binder"
    SCRIPTS = ROOT / "_scripts"

    CONDARC = GITHUB / ".condarc"
    PACKAGE_JSON = SCRIPTS / "package.json"
    YARNRC = SCRIPTS / ".yarnrc"
    PYPROJECT = SCRIPTS / "pyproject.toml"
    README = ROOT / "README.md"
    CHANGELOG = ROOT / "CHANGELOG.md"

    # generated, but checked in
    YARN_LOCK = SCRIPTS / "yarn.lock"
    WORKFLOW = GITHUB / "workflows/ci.yml"
    LOCKS = ROOT / "locks"
    CONSTRUCTS = ROOT / "constructs"

    # stuff we don't check in
    BUILD = ROOT / "build"
    ATEST_OUT = BUILD / "atest"
    AUDIT_OUT = BUILD / "audit"
    DIST = ROOT / "dist"
    NODE_MODULES = SCRIPTS / "node_modules"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"
    CACHE = SCRIPTS / ".cache"
    CONSTRUCTOR_CACHE = Path(
        os.environ.get("CONSTTRUCTOR_CACHE", CACHE / "constructor")
    )

    # config cruft
    YARN = ["yarn"]
    PRETTIER_SUFFIXES = [".yml", ".yaml", ".json", ".md"]
    PRETTIERRC = SCRIPTS / ".prettierrc"
    PRETTIER = [
        *YARN,
        "prettier",
        "--config",
        PRETTIERRC,
        "--list-different",
        "--write",
    ]

    # collections of things
    ALL_PY = [DODO, *SCRIPTS.glob("*.py")]
    ALL_ROBOT = [*ATEST.rglob("*.robot")]
    ALL_YAML = [
        *SPECS.glob("*.yml"),
        *GITHUB.rglob("*.yml"),
        *CONSTRUCTS.glob("*.yaml"),
        *BINDER.glob("*.yml"),
    ]
    ALL_SH = [
        *BINDER.glob("*.sh"),
        *CONSTRUCTS.glob("*/*.sh"),
        BINDER / "postBuild",
        *GITHUB.rglob("*.sh"),
    ]
    ALL_BAT = [*CONSTRUCTS.glob("*/*.bat")]
    ALL_MD = [*ROOT.glob("*.md")]
    ALL_JSON = [*TEMPLATES.rglob("*.json"), *SCRIPTS.glob("*.js")]
    ALL_PRETTIER = [
        *ALL_JSON,
        *ALL_MD,
        *ALL_YAML,
        *SCRIPTS.glob("*.json"),
        CONDARC,
    ]
    ALL_HEADER_FILES = [*ALL_MD, *ALL_YAML, *ALL_PY, *ALL_ROBOT, *ALL_SH, *ALL_BAT]


class C:
    """constants"""

    NAME = "GTCOARLab"
    ENC = dict(encoding="utf-8")
    VARIANTS = ["cpu", "gpu"]
    SUBDIRS = ["linux-64", "osx-64", "win-64"]
    THIS_SUBDIR = {"Linux": "linux-64", "Darwin": "osx-64", "Windows": "win-64"}[
        platform.system()
    ]
    TODAY = datetime.today()
    YEAR = TODAY.strftime("%Y")
    VERSION = P.VERSION.read_text(encoding="utf-8").strip()
    CONSTRUCTOR_PLATFORM = {
        "linux-64": ["Linux-x86_64", "sh"],
        "osx-64": ["MacOSX-x86_64", "sh"],
        "win-64": ["Windows-x86_64", "exe"],
    }
    VM = {
        "linux-64": "ubuntu-20.04",
        "osx-64": "macos-latest",
        "win-64": "windows-latest",
    }
    CI = bool(safe_load(os.environ.get("CI", "0")))
    CI_LINTING = bool(safe_load(os.environ.get("CI_LINTING", "0")))
    SKIP_LOCKS = CI
    SKIP_LINT = CI and not CI_LINTING
    CHUNKSIZE = 8192

    ATEST_RETRIES = int(os.environ.get("ATEST_RETRIES", "0"))
    ATEST_ARGS = safe_load(os.environ.get("ATEST_ARGS", "[]"))
    AUTHORS = "University System of Georgia and GTCOARLab Contributors"
    COPYRIGHT_HEADER = f"Copyright (c) {YEAR} {AUTHORS}"
    LICENSE = "BSD-3-Clause"
    LICENSE_HEADER = f"Distributed under the terms of the {LICENSE} License"


class U:
    """utilities"""

    cmd = lambda *args, **kwargs: CmdAction(*args, **kwargs, shell=False)
    script = lambda *args, **kwargs: U.cmd(*args, **kwargs, cwd=str(P.SCRIPTS))

    @classmethod
    def variant_spec(cls, variant, subdir):
        spec = P.SPECS / f"run-{variant}-{subdir}.yml"
        return spec if spec.exists() else None

    @classmethod
    def installer(cls, variant, subdir):
        pf, ext = C.CONSTRUCTOR_PLATFORM[subdir]
        name = f"{C.NAME}-{variant.upper()}-{C.VERSION}-{pf}.{ext}"
        return P.DIST / name

    @classmethod
    def construct(cls, variant, subdir):
        construct = P.CONSTRUCTS / f"{variant}-{subdir}"
        lock = P.LOCKS / f"run-{variant}-{subdir}.conda.lock"
        tmpl_dir = P.TEMPLATES / "construct"
        templates = tmpl_dir.rglob("*")
        overrides = P.TEMPLATES / "overrides.json"
        paths = {
            t: construct / (str(t.relative_to(tmpl_dir)).replace(".j2", ""))
            for t in templates
        }

        paths = {
            k: v
            for k, v in paths.items()
            if not any(
                [
                    (subdir == "win-64" and v.name.endswith(".sh")),
                    (subdir != "win-64" and v.name.endswith(".bat")),
                ]
            )
        }

        def construct():
            overrides_text = json.dumps(
                json.loads(overrides.read_text(encoding="utf-8"))
            )
            context = dict(
                specs=lock.read_text(**C.ENC)
                .split("@EXPLICIT")[1]
                .strip()
                .splitlines(),
                name=C.NAME,
                subdir=subdir,
                variant=variant,
                version=C.VERSION,
                copyright=C.COPYRIGHT_HEADER,
                license=C.LICENSE_HEADER,
                # we _want_ python-compatible, single quotes,
                settings_path="share/jupyter/lab/settings",
                overrides=overrides_text,
                # windows is special
                win_settings_path="share\\jupyter\\lab\\settings",
            )
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
                    U.script([*P.PRETTIER, dest_path]).execute()

        yield dict(
            name=f"{variant}:{subdir}",
            actions=[construct],
            file_dep=[P.VERSION, lock, overrides, *paths.keys()],
            targets=[*paths.values()],
        )

    @classmethod
    def build(cls, variant, subdir):
        construct = P.CONSTRUCTS / f"{variant}-{subdir}"
        installer = U.installer(variant, subdir)
        hashfile = installer.parent / f"{installer.name}.sha256"

        args = [
            "constructor",
            ".",
            "--debug",
            "--output-dir",
            P.DIST,
            "--cache-dir",
            P.CONSTRUCTOR_CACHE,
        ]

        env = dict(os.environ)

        env.update(CONDA_EXE="mamba", CONDARC=str(P.CONDARC))

        def build():
            proc = subprocess.Popen(list(map(str, args)), cwd=str(construct), env=env)
            try:
                rc = proc.wait()
            except KeyboardInterrupt:
                proc.terminate()
                rc = 1

            return rc == 0

        yield dict(
            name=f"{variant}:{subdir}",
            actions=[(create_folder, [P.DIST]), build],
            file_dep=[*construct.rglob("*")],
            targets=[installer],
        )

        yield dict(
            name=f"{variant}:{subdir}:sha256",
            actions=[(U.sha256, [hashfile, installer])],
            file_dep=[installer],
            targets=[hashfile],
        )

    @classmethod
    def sha256(cls, hashfile, *paths):
        with hashfile.open("w+") as hfp:
            for path in sorted(paths):
                h = sha256()
                with path.open("rb") as fp:
                    for byte_block in iter(lambda: fp.read(C.CHUNKSIZE), b""):
                        h.update(byte_block)

                hfp.write(f"{h.hexdigest()}  {path.name}")

    @classmethod
    def atest(cls, variant, subdir):
        return_code = 1
        for attempt in range(C.ATEST_RETRIES + 1):
            return_code = U.atest_attempt(variant, subdir, attempt)
            if return_code == 0:
                break
        U.rebot()
        return return_code == 0

    @classmethod
    def atest_attempt(cls, variant, subdir, attempt):
        extra_args = []

        installer = U.installer(variant, subdir)
        stem = f"{variant}-{subdir}-{attempt}"
        out_dir = P.ATEST_OUT / stem
        inst_dir = P.BUILD / f"{variant}-{subdir}"

        if out_dir.exists():
            try:
                shutil.rmtree(out_dir)
            except Exception as err:
                log.error(err)

        out_dir.mkdir(parents=True, exist_ok=True)

        if attempt:
            extra_args += ["--loglevel", "TRACE"]
            previous = P.ATEST_OUT / f"{variant}-{subdir}-{attempt - 1}.robot.xml"
            if previous.exists():
                extra_args += ["--rerunfailed", str(previous)]

        extra_args += C.ATEST_ARGS

        variables = dict(
            ATTEMPT=attempt,
            INST_DIR=inst_dir,
            INSTALLER=installer,
            NAME=installer.name,
            OS=platform.system(),
            OVERRIDES=P.TEMPLATES / "overrides.json",
            VARIANT=variant,
            VERSION=C.VERSION,
        )

        extra_args += sum(
            [["--variable", f"{key}:{value}"] for key, value in variables.items()], []
        )

        args = [
            "--name",
            f"{C.NAME} {variant} {subdir}",
            "--outputdir",
            out_dir,
            "--output",
            P.ATEST_OUT / f"{stem}.robot.xml",
            "--log",
            P.ATEST_OUT / f"{stem}.log.html",
            "--report",
            P.ATEST_OUT / f"{stem}.report.html",
            "--xunit",
            P.ATEST_OUT / f"{stem}.xunit.xml",
            "--randomize",
            "all",
            *extra_args,
            # the folder must always go last
            P.ATEST,
        ]

        str_args = ["python", "-m", "robot", *map(str, args)]
        log.warning(">>> %s", " ".join(str_args))
        proc = subprocess.Popen(str_args, cwd=P.ATEST)

        try:
            return proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            return 1

    @classmethod
    def attempt_lock(cls, args):
        for solver in [["--mamba"], []]:
            solver_args = ["conda-lock", *solver, *args]
            str_args = list(map(str, solver_args))
            print(" ".join(str_args))
            solver_rc = subprocess.call(str_args, cwd=str(P.LOCKS))
            if solver_rc == 0:
                break

        return solver_rc == 0

    @classmethod
    def lock(cls, env_name, variant, subdir, extra_env_names=[], include_base=True):
        args = ["--platform", subdir]
        stem = env_name + (f"-{variant}-" if variant else "-") + subdir
        lockfile = P.LOCKS / f"{stem}.conda.lock"

        specs = []

        if include_base:
            specs += [P.SPECS / "_base.yml"]

        for env in [env_name, *extra_env_names]:
            for fname in [f"{env}", f"{env}-{subdir}", f"{env}-{variant}-{subdir}"]:
                spec = P.SPECS / f"{fname}.yml"
                if spec.exists():
                    specs += [spec]

        args += sum([["--file", spec] for spec in specs], [])
        args += [
            "--filename-template",
            env_name + (f"-{variant}-" if variant else "-") + "{platform}.conda.lock",
        ]
        return dict(
            name=f"""{env_name}:{variant or ""}:{subdir}""",
            file_dep=specs,
            actions=[
                (create_folder, [P.LOCKS]),
                (U.attempt_lock, [args]),
            ],
            targets=[lockfile],
        )

    @classmethod
    def rebot(cls):
        args = [
            "python",
            "-m",
            "robot.rebot",
            "--name",
            "🤖",
            "--nostatusrc",
            "--merge",
            "--output",
            P.ATEST_OUT / "robot.xml",
            "--log",
            P.ATEST_OUT / "log.html",
            "--report",
            P.ATEST_OUT / "report.html",
            "--xunit",
            P.ATEST_OUT / "xunit.xml",
        ] + sorted(P.ATEST_OUT.glob("*.robot.xml"))

        str_args = [*map(str, args)]

        log.warning(">>> rebot args: %s", " ".join(str_args))

        proc = subprocess.Popen(str_args)

        try:
            return proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            return 1

    @classmethod
    def headers(cls, path):
        text = path.read_text(**C.ENC)
        for header in [C.COPYRIGHT_HEADER, C.LICENSE_HEADER]:
            if header not in text:
                log.error(f"{path} needs {header}")
                return False

    @classmethod
    def audit(cls, variant, subdir):
        args = ["python", P.SCRIPTS / "audit.py", P.ATEST_OUT / f"{variant}-{subdir}-0"]
        str_args = [*map(str, args)]
        proc = subprocess.Popen(str_args)
        audit_rc = proc.wait()
        return audit_rc == 0


class R(ConsoleReporter):
    TIMEFMT = "%H:%M:%S"
    SKIP = " " * len(TIMEFMT)
    _timings = {}
    ISTOP = "🛑"
    ISTART = "🔬"
    ISKIP = "⏩"
    IPASS = "🎉"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute_task(self, task):
        start = datetime.now()
        title = task.title()
        self._timings[title] = [start]
        self.outstream.write(
            f"""{R.ISTART} {start.strftime(R.TIMEFMT)}   START  {title}\n"""
        )

    def outtro(self, task, emoji, status):
        title = task.title()
        start, end = self._timings[title] = [
            *self._timings[title],
            datetime.now(),
        ]
        delta = end - start
        sec = str(delta.seconds).rjust(7)
        self.outstream.write(f"{emoji}  {sec}s   {status}  {task.title()}\n")

    def add_failure(self, task, exception):
        super().add_failure(task, exception)
        self.outtro(task, R.ISTOP, "FAIL")

    def add_success(self, task):
        super().add_success(task)
        self.outtro(task, R.IPASS, "PASS")

    def skip_uptodate(self, task):
        self.outstream.write(f"{R.ISKIP} {R.SKIP}    SKIP      {task.title()}\n")

    skip_ignore = skip_uptodate


# HACKS

DOIT_CONFIG = {
    "backend": "sqlite3",
    "verbosity": 2,
    "par_type": "thread",
    "reporter": R,
}

# patch environment for all child tasks
os.environ.update(
    CONDARC=str(P.CONDARC),
    MAMBA_NO_BANNER="1",
    PYTHONUNBUFFERED="1",
    PYTHONIOENCODING="utf-8",
)

# for windows, mostly, but whatever
colorama.init()
