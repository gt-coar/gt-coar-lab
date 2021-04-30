# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

*** Settings ***
Documentation     Does The starter show?
Resource          ../_resources/Lab.robot
Test Setup        Wait for GTCOARLab to Open

*** Test Cases ***
Reinforcement Learning
    [Documentation]    Did the starter survive the installation?
    # ignore the active cell error
    Run Keyword and Ignore Error    Launch a New JupyterLab Document
    ...    reinforcement-learning. dennybritz, 2019.11.0
    ...    category=Starters
    ${sel} =    Set Variable    css:#id-jp-schemaform-0_ready
    Wait Until Page Contains Element    ${sel}
    Execute JavaScript    document.querySelector('.jp-SchemaForm').scrollTop = 9999
    Click Element    ${sel}
    Start the Starter
    Wait Until Page Contains    README.md
    Capture Page Screenshot    01-00-reinforcement-learning-started.png

*** Keywords ***
Start the Starter
    [Documentation]    Nastily clobber toasts, run the starter
    Execute JavaScript
    ...    (el = document.querySelector('.jp-toastContainer')) && el.remove()
    Click Element    css:.jp-mod-accept
