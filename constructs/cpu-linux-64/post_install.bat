:: Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
:: Distributed under the terms of the BSD-3-Clause License
::
:: GTCOARLab-CPU 2021.03-0
::
@ECHO ON

set POST_INSTALL_LOG=%PREFIX%\post_install.log

echo "start" >> %POST_INSTALL_LOG%

md /s /q "%PREFIX%\share\jupyter\lab\settings" ^
    || echo 'directory might already exist' ^
    >> "%POST_INSTALL_LOG%"

echo ^
    "{""@jupyterlab/apputils-extension:themes"": {""theme"": ""GT COAR Dark"", ""theme-scrollbars"": true}, ""jupyterlab/terminal-extension:plugin"": {""fontFamily"": ""'Roboto Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace"", ""fontSize"": 14}, ""@jupyterlab/filebrowser-extension:browser"": {""navigateToCurrentDirectory"": true}}" ^
    > "%PREFIX%\share\jupyter\lab\settings\overrides.json" ^
    || echo "failed to write overrides" ^ 
    >> %POST_INSTALL_LOG%

echo "done" >> %POST_INSTALL_LOG%