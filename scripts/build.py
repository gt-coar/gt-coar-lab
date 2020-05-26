import subprocess
import jinja2
import pathlib
import ruamel_yaml
import sys
from constructor.conda_interface import cc_platform
from datetime import datetime

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
INSTALLER = ROOT / "installer"
TMPL = INSTALLER / "construct.yaml.j2"
CONSTRUCT = INSTALLER / "construct.yaml"
PROJ = ROOT / "anaconda-project.yml"
LOCK = ROOT / "anaconda-project-lock.yml"
ENV = "coar-lab"
DIST = ROOT / "dist"
CACHE = ROOT / ".cache"
CONSTRUCTOR_CACHE = CACHE / "constructor"

PLATFORMS = ["all", cc_platform]

if not cc_platform.startswith("win-"):
    PLATFORMS += ["unix"]


def template():
    """ Build a construct.yaml from the project file, lock file
    """
    lock = ruamel_yaml.safe_load(LOCK.read_text())
    proj = ruamel_yaml.safe_load(PROJ.read_text())
    env = lock
    tmpl = jinja2.Template(TMPL.read_text())
    today = datetime.today()
    packages = lock["env_specs"][ENV]["packages"]
    context = dict(
        version=f"{today.year}.{today.month}.{today.day}",
        channels=proj["env_specs"][ENV]["channels"],
        specs=sorted(sum([packages.get(p, []) for p in PLATFORMS], []))
    )
    CONSTRUCT.write_text(tmpl.render(**context))
    return 0


def build():
    """ Build an installer from the generated construct.yaml
    """
    args = list(map(str, [
        "constructor", ".",
        "--output-dir", DIST.resolve(),
        "--cache-dir", CONSTRUCTOR_CACHE.resolve(),
    ]))
    return subprocess.call(args, cwd=str(INSTALLER))


if __name__ == "__main__":
    sys.exit(template() or build())
