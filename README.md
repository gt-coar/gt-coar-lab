# GTCOARLab

_an environment for interactive exploration of reinforcement learning_

|                Build                 |               Interactive Demo               |
| :----------------------------------: | :------------------------------------------: |
| [![view latest build][ci-badge]](ci) | [![launch demo on binder][demo-badge]][demo] |

[![a screenshot of GTCOARLab running gym-atari on mybinder.org][screenshot]][screenshot-issue]

## Downloading GTCOARLab

- View the [releases] on GitHub
- Choose the right artifacts for your operating system and hardware
  - CPU: does not require a CUDA-capable graphics card and drivers
  - GPU: some features require a CUDA-capable graphics card and drivers
- Download the artifacts (they are big, it will take a while)
  > - If your platform contains multiple `.zip` and `.z01`, `.z02` files, you need to
  >   download them all
  >   - a GUI or the `zip` command line tool will know how to decompress them correctly
  >     by using the `.zip` file, which should be smaller than the others
- Follow the instructions for e.g. [miniconda][miniconda-install]
  - on Windows, prefer installing to a _short path_ on a _fast device_ (e.g. SSD) such
    as `C:/gtcl`
  - if you've already installed Anaconda, Miniconda, or Miniforge, it is recommended to
    _not_ enable _shell integration_, _environment variables_, or _registering as the
    default Python_
- From the command line, _activate_ the environment
  > - on Windows, you should see a _Start Menu_ entry
  - run `jupyter lab`, and you should see the JupyterLab interface open in your default
    browser with
    - to choose your browser, start `jupyter lab --no-browser` and copy/paste the URL
      shown into your browser of choice
- If you run into problems, create an [issue] on GitHub

[ci]: https://github.com/gt-coar/gt-coar-lab/actions
[ci-badge]: https://github.com/gt-coar/gt-coar-lab/workflows/CI/badge.svg
[demo-badge]: https://mybinder.org/badge_logo.svg
[demo]:
  https://mybinder.org/v2/gh/gt-coar/gt-coar-lab/master?urlpath=lab/notebooks/Headless%20Gym.ipynb
[screenshot]:
  https://user-images.githubusercontent.com/7581399/111483945-ab1b1180-870b-11eb-8ce3-2bd81b205733.png
[screenshot-issue]: https://github.com/gt-coar/gt-coar-lab/issues/16
[miniconda-install]:
  https://conda.io/projects/conda/en/latest/user-guide/install/index.html
[releases]: https://github.com/gt-coar/gt-coar-lab/releases
[issue]: https://github.com/gt-coar/gt-coar-lab/issues

> Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
>
> Distributed under the terms of the BSD-3-Clause License
