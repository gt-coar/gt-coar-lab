# Contributing to GTCOARLab

## Set Up

- Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Python 3
- Create the base env

```bash
conda env update --file .ci_support/environment-base.yml
```

- always run any commands with that environment activated

```bash
source ~/miniconda3/envs/gt-coar-lab-base/bin/activate
```

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

- `*` may be used as a wildcard

## Updating dependencies

One notable task that doesn't occur in the `doit` flow is updating dependencies.

After changing a dependency in `anaconda-project.yml`:

```bash
python -m scripts.update
```

---

> Copyright (c) 2020 University System of Georgia and GTCOARLab Contributors
>
> Distributed under the terms of the BSD-3-Clause License
