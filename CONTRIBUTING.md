# Contributing to GTCOARLab

## Set Up

- Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Python 3
- Create the core env

```bash
conda env update --file .ci_support/environment-base.yml
```

- follow the instructions, and always run the commands below from that env

## doit

[doit](https://github.com/pydoit/doit) drives local development, usually by calling
[anaconda-project](https://github.com/Anaconda-Platform/anaconda-project) commands.

To list all the tasks that you _could_ run:

```bash
doit list
```

To run _everything that needs to be run_:

```bash
doit
```

## Updating dependencies

One notable task that doesn't occur in the default flow is updating the installer
dependencies.

After changing a dependency in `anaconda-project.yml`, run:

```bash
python -m scripts.update   # updates the lock file
doit lint*                 # fixes whitespace
```

---

> Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
>
> Distributed under the terms of the BSD-3-Clause License
