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
  - the `VERSION` file
  - any file in `constructs/<variant>-<subdir>`
  - the platform-specific `locks/build-<subdir>.conda.lock` file
  - the `CACHE_EPOCH` (ideally, only by _increasing_)

### releasing

- Wait for a successful merge to `master`
- Through the _GitHub Web UI_, create a _Release_
  - name the release _the same thing_ as the current value of the `VERSION` file, with a
    `v` prepended
    - only these will trigger the (slow) upload mechanism
  - creating/pushing a local tag will fail, as the `release` job expects the release id
    to already exist in the GitHub API _before_ uploading artifacts
  - it should build/upload relatively quickly, as the built artifacts _should_ still be
    in the cache.
  - _shipping is good_, but marking a new tag as a _prerelease_ allows the release
    upload script to complete, and the release assets can be more easily tested.
- After the `release` job completes, add the uploaded `NOTES.md` to the release page.

---

> Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
>
> Distributed under the terms of the BSD-3-Clause License
