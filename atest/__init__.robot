*** Settings ***
Documentation     Basic tests of GTCOARLab installer
Library           OperatingSystem
Force Tags        os:${OS}    version:${VERSION}
Suite Setup       Run Installer

*** Keywords ***
Run Installer
    [Documentation]    Run the installer
    File Should Exist    ${INSTALLER}
    Log    It's
    Log    all
    Log    good
