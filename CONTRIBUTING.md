# Contributing to GTCOARLab

## Set Up

- Install [Mambaforge](https://github.com/conda-forge/miniforge/releases)
- Create the base environment

```bash
CONDARC=.github/.condarc mamba create --file locks/dev-linux-64.conda.lock --prefix .venv
```

- always run any commands with that environment activated

```bash
source .venv/bin/activate
```

## doit

[doit](https://github.com/pydoit/doit) drives local development.

To list all the tasks that you _could_ run:

```bash
doit list
```

To run _everything that needs to be run_:

```bash
doit
```

- `*` may be used as a wildcard

## ci

Building, testing, and even releasing the GTCOARLab installers is a _heavy_ continuous
integration task. The `.github/workflows/ci.yml` is quite verbose, and is actually
generated from a number of other files, to allow for (relatively) quick testing, if only
only tests or release scripts change.

Some notes:

- the installers should only be rebuilt when one of the following changes:
  - any file in `constructs/<variant>-<subdir>`
  - the platform-specific `locks/build-<subdir>.conda.lock` file
  - the `CACHE_EPOCH` (ideally, only by _increasing_)

### releasing

After a successful merge to `master` and the workflow completes, a tag should
test/release relatively quickly, as the built artifacts should still be in the cache.

While not required, because _shipping is good_, marking a new tag as a _prerelease_
allows the release upload script to work, and the release assets can be more easily
tested.

After the release job completes, the uploaded `NOTES.md` are ideally added to the
release page.

---

> Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
>
> Distributed under the terms of the BSD-3-Clause License
