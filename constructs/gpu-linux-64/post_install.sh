# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
#
# GTCOARLab-GPU 2021.03-0 defaults
#
set -x

python -c "\
    import os, json, pathlib.Path as P;                                         \
    overrides = P(os.environ['PREFIX']) / 'share/jupyter/lab/settings/overrides.json'; \
    overrides.parent.mkdir(parents=True, exist_ok=True);                        \
    overrides.write_text(json.dumps({'@jupyterlab/apputils-extension:themes': {'theme': 'GT COAR Dark', 'theme-scrollbars': True}, 'jupyterlab/terminal-extension:plugin': {'fontFamily': "'Roboto Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace", 'fontSize': 14}, '@jupyterlab/filebrowser-extension:browser': {'navigateToCurrentDirectory': True}}));                          \
"