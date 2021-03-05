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
