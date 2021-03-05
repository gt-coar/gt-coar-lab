*** Settings ***
Documentation     Install an Installer
Library           OperatingSystem
Library           Process
Resource          ./Cleanup.robot
Resource          ./Variables.robot
Resource          ./Shell.robot

*** Keywords ***
Maybe Run the Installer
    [Documentation]    Run the installer, if not already installed
    ${history} =    Normalize Path    ${INST DIR}${/}conda-meta${/}history
    ${installed} =    Evaluate    __import__('os.path').path.exists(r"""${history}""")
    Run Keyword If    ${installed}
    ...    Log    Already installed!
    ...    ELSE
    ...    Run The Installer
    Validate the Installation

Run the Installer
    [Documentation]    Run the platform-specific installer
    File Should Exist    ${INSTALLER}
    ${path} =    Set Variable    ${OUTPUT DIR}
    Set Global Variable    ${HOME}    ${path}${/}home
    ${rc} =
    ...    Run Keyword If    "${OS}" == "Linux"
    ...    Run the Linux Installer
    ...    ELSE IF    "${OS}" == "Windows"
    ...    Run the Windows Installer
    ...    ELSE IF    "${OS}" == "Darwin"
    ...    Run the MacOSX Installer
    ...    ELSE
    ...    Fatal Error    Can't install on platform ${OS}!
    Should Be Equal as Integers    ${rc}    0
    ...    msg=Couldn't complete installer, see ${INSTALL LOG}

Validate the Installation
    [Documentation]    Ensure some baseline commands work
    Wait Until Keyword Succeeds    5x    30s
    ...    Run Shell Script in Installation
    ...    mamba info
    Wait Until Keyword Succeeds    5x    30s
    ...    Run Shell Script in Installation
    ...    mamba list
    Run Shell Script in Installation
    ...    python -m pip freeze
    Run Shell Script in Installation
    ...    mamba list --explicit

Run the Linux installer
    [Documentation]    Install on Linux
    Set Global Variable    ${ACTIVATE SCRIPT}    ${INST DIR}${/}bin${/}activate
    Set Global Variable    ${ACTIVATE}    . "${ACTIVATE SCRIPT}" "${INST DIR}" && set -eux
    Set Global Variable    ${PATH ENV}    ${INST DIR}${/}bin:%{PATH}
    ${result} =    Run Process    bash    ${INSTALLER}    -fbp    ${INST DIR}
    ...    stdout=${INSTALL LOG}    stderr=STDOUT
    [Return]    ${result.rc}

Run the MacOSX installer
    [Documentation]    Install on OSX
    Set Global Variable    ${ACTIVATE SCRIPT}    ${INST DIR}${/}bin${/}activate
    Set Global Variable    ${ACTIVATE}    . "${ACTIVATE SCRIPT}" "${INST DIR}"
    Set Global Variable    ${PATH ENV}    ${INST DIR}${/}bin${:}%{PATH}
    ${result} =    Run Process    bash    ${INSTALLER}    -fbp    ${INST DIR}
    ...    stdout=${INSTALL LOG}    stderr=STDOUT
    [Return]    ${result.rc}

Run the Windows installer
    [Documentation]    Install on Windows
    Set Global Variable    ${ACTIVATE SCRIPT}    ${INST DIR}${/}Scripts${/}activate.bat
    Set Global Variable    ${ACTIVATE}    call "${ACTIVATE SCRIPT}" "${INST DIR}"
    Set Global Variable    ${PATH ENV}
    ...    ${INST DIR}${:}${INST DIR}${/}Scripts${:}${INST DIR}${/}Library${/}bin${:}%{PATH}
    ${args} =    Set Variable
    ...    /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=${INST DIR}
    ${result} =    Run Process    start /wait "" ${INSTALLER} ${args}
    ...    stdout=${INSTALL LOG}    stderr=STDOUT    shell=True
    [Return]    ${result.rc}

Get GeckoDriver
    [Documentation]    Get the path to the bundled geckodriver
    ${path} =    Set Variable    ${INST DIR}${/}&{GECKODRIVER}[${OS}]
    File Should Exist    ${path}
    [Return]    ${path}

Get Firefox
    [Documentation]    Get the path to the bundled firefox
    ${path} =    Set Variable    ${INST DIR}${/}${FIREFOX}[${OS}]
    File Should Exist    ${path}
    [Return]    ${path}
