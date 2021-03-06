*** Settings ***
Documentation     Install an Installer
Library           OperatingSystem
Library           Process
Resource          ./Cleanup.robot
Resource          ./Variables.robot
Resource          ./Shell.robot

*** Keywords ***
Run the Installer
    [Documentation]    Run the platform-specific installer
    File Should Exist    ${INSTALLER}
    ${installation} =    Normalize Path    ${CURDIR}${/}..${/}..${/}tmp${/}${NAME}_${ATTEMPT}
    ${path} =    Set Variable    ${OUTPUT DIR}
    Set Global Variable    ${INSTALLATION}    ${installation}
    Set Global Variable    ${HOME}    ${path}${/}home
    ${rc} =    Run Keyword If    "${OS}" == "Linux"    Run the Linux Installer
    ...    ELSE IF    "${OS}" == "Windows"    Run the Windows Installer
    ...    ELSE IF    "${OS}" == "MacOSX"    Run the MacOSX Installer
    ...    ELSE    Fatal Error    Can't install on platform ${OS}!
    Should Be Equal as Integers    ${rc}    0    msg=Couldn't complete installer, see ${INSTALL LOG}
    Wait Until Keyword Succeeds    5x    30s    Run Shell Script in Installation    conda info && conda list
    Run Shell Script in Installation    pip freeze > ${OUTPUT DIR}${/}requirements.txt
    Run Shell Script in Installation    conda list --explicit > ${OUTPUT DIR}${/}conda-explicit.txt

Run the Linux installer
    [Documentation]    Install on Linux
    Set Global Variable    ${ACTIVATE SCRIPT}    ${INSTALLATION}${/}bin${/}activate
    Set Global Variable    ${ACTIVATE}    . "${ACTIVATE SCRIPT}" "${INSTALLATION}" && set -eux
    Set Global Variable    ${PATH ENV}    ${INSTALLATION}${/}bin:%{PATH}
    ${result} =    Run Process    bash    ${INSTALLER}    -fbp    ${INSTALLATION}
    ...    stdout=${INSTALL LOG}    stderr=STDOUT
    [Return]    ${result.rc}

Run the MacOSX installer
    [Documentation]    Install on OSX
    Set Global Variable    ${ACTIVATE SCRIPT}    ${INSTALLATION}${/}bin${/}activate
    Set Global Variable    ${ACTIVATE}    . "${ACTIVATE SCRIPT}" "${INSTALLATION}"
    Set Global Variable    ${PATH ENV}    ${INSTALLATION}${/}bin${:}%{PATH}
    ${result} =    Run Process    bash    ${INSTALLER}    -fbp    ${INSTALLATION}
    ...    stdout=${INSTALL LOG}    stderr=STDOUT
    [Return]    ${result.rc}

Run the Windows installer
    [Documentation]    Install on Windows
    Set Global Variable    ${ACTIVATE SCRIPT}    ${INSTALLATION}${/}Scripts${/}activate.bat
    Set Global Variable    ${ACTIVATE}    call "${ACTIVATE SCRIPT}" "${INSTALLATION}"
    Set Global Variable    ${PATH ENV}
    ...    ${INSTALLATION}${:}${INSTALLATION}${/}Scripts${:}${INSTALLATION}${/}Library${/}bin${:}%{PATH}
    ${args} =    Set Variable    /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=${INSTALLATION}
    ${result} =    Run Process    start /wait "" ${INSTALLER} ${args}
    ...    stdout=${INSTALL LOG}    stderr=STDOUT    shell=True
    [Return]    ${result.rc}

Get GeckoDriver
    [Documentation]    Get the path to the bundled geckodriver
    ${path} =    Set Variable    ${INSTALLATION}${/}&{GECKODRIVER}[${OS}]
    File Should Exist    ${path}
    [Return]    ${path}

Get Firefox
    [Documentation]    Get the path to the bundled firefox
    ${path} =    Set Variable    ${INSTALLATION}${/}${FIREFOX}[${OS}]
    File Should Exist    ${path}
    [Return]    ${path}
