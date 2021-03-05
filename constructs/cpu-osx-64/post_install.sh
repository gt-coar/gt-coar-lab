# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
#
# GTCOARLab-CPU 2021.03-0 defaults
#
set -x

export settings="$PREFIX/share/jupyter/lab/settings"
export overrides="$settings/overrides.json"

mkdir -p $settings

cat << EOF > "$overrides"
{'@jupyterlab/apputils-extension:themes': {'theme': 'GT COAR Dark', 'theme-scrollbars': True}, 'jupyterlab/terminal-extension:plugin': {'fontFamily': "'Roboto Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace", 'fontSize': 14}, '@jupyterlab/filebrowser-extension:browser': {'navigateToCurrentDirectory': True}}
EOF