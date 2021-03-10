# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
#
# GTCOARLab-GPU 2021.03-0 defaults
#
set -x

export POST_INSTALL_LOG="${PREFIX}/post_install.log"

echo "start" >> "${POST_INSTALL_LOG}"
ls "${PREFIX}/share/jupyter/lab/settings"  || echo "probably ok"
mkdir -p "${PREFIX}/share/jupyter/lab/settings" || echo "settings path probably exists"

cat << EOF > "${PREFIX}/share/jupyter/lab/settings/overrides.json"
{"@jupyterlab/apputils-extension:themes": {"theme": "GT COAR Dark", "theme-scrollbars": true}, "jupyterlab/terminal-extension:plugin": {"fontFamily": "'Roboto Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace", "fontSize": 14}, "@jupyterlab/filebrowser-extension:browser": {"navigateToCurrentDirectory": true}}
EOF

echo "done" >> "${POST_INSTALL_LOG}"