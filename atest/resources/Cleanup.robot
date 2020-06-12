*** Settings ***
Library           OperatingSystem
Library           Process

*** Keywords ***
Clean up the Installation
    [Documentation]    Clean out the installation
    Terminate All Processes
    Sleep    5s
    Terminate All Processes    kill=True
    Sleep    5s
    Remove Directory    ${INSTALLATION}    recursive=True
    Sleep    5s
    Remove Directory    ${INSTALLATION}    recursive=True
