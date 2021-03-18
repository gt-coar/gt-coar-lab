# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

*** Settings ***
Library           JupyterLibrary
Library           OperatingSystem
Library           Process

*** Keywords ***
Clean up the Test
    [Documentation]    Clean up the test (leave the installation)
    Terminate All Jupyter Servers
    Terminate All Processes
    Terminate All Processes    kill=True
