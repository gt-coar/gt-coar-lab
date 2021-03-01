# Contributing to GTCOARLab

## Set Up

- Install [Mambaforge](https://github.com/conda-forge/miniforge/releases)
- Create the base environment, using the same environment/configuration as CI

```bash
CONDARC=.github/.condarc mamba env update --file .github/environment.yml --prefix .env
```

- always run any commands with that environment activated

```bash
source .env/bin/activate
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

---

> Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
>
> Distributed under the terms of the BSD-3-Clause License
