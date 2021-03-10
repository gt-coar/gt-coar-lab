:: Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
:: Distributed under the terms of the BSD-3-Clause License
::
:: GTCOARLab-CPU 2021.03-0
::
@ECHO ON

set "POST_INSTALL_LOG=%PREFIX%\post_install.log"
set "SETTINGS_PATH=%PREFIX%\share\jupyter\lab\settings"
set "OVERRIDES_PATH=%SETTINGS_PATH%\overrides.json"

echo "0.0: start" >> "%POST_INSTALL_LOG%"

md /s /q "%SETTINGS_PATH%" || echo "0.1: directory might already exist" >> "%POST_INSTALL_LOG%"

echo "1.0: (maybe) ensured %SETTINGS_PATH%" >> "%POST_INSTALL_LOG%"

dir %SETTINGS_PATH% >> "%POST_INSTALL_LOG%" 2>&1 || echo "1.1: might have failed to list settings" >> "%POST_INSTALL_LOG%"

set "OVERRIDES={""@jupyterlab/apputils-extension:themes"": {""theme"": ""GT COAR Dark"", ""theme-scrollbars"": true}, ""jupyterlab/terminal-extension:plugin"": {""fontFamily"": ""'Roboto Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace"", ""fontSize"": 14}, ""@jupyterlab/filebrowser-extension:browser"": {""navigateToCurrentDirectory"": true}}"

echo "2.0: created overrides env var for %OVERRIDES%" >> "%POST_INSTALL_LOG%"

echo "%OVERRIDES%" > "%OVERRIDES_PATH%" || echo "2.1: failed to write overrides" >> "%POST_INSTALL_LOG%"

dir "%SETTINGS_PATH%" >> "%POST_INSTALL_LOG%" 2>&1 || echo "2.1: might have failed to list settings" >> "%POST_INSTALL_LOG%"

echo "3.0: maybe wrote overrides" >> "%POST_INSTALL_LOG%"

type "%OVERRIDES_PATH%" >> "%POST_INSTALL_LOG%" || echo "3.0: might have failed to log settings" >> "%POST_INSTALL_LOG%"

echo "4.0: done" >> "%POST_INSTALL_LOG%"