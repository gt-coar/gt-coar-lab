# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
#
# GTCOARLab-CPU 2021.03-0 defaults
#
set -x

export settings="$PREFIX/share/jupyter/lab/user-settings/@jupyterlab"
export apputils="$settings/apputils-extension"
export term="$settings/terminal-extension"

mkdir -p $apputils $term

cat << EOF > "$apputils/themes.jupyterlab-settings"
{"theme": "GT COAR Light", "theme-scrollbars": true}
EOF

cat << EOF > "$apputils/themes.jupyterlab-settings"
{
  "fontFamily": "\"Roboto Mono\", Menlo, Consolas, \"DejaVu Sans Mono\", monospace",
  "fontSize": 14
}
EOF