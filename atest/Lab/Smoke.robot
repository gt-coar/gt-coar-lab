*** Settings ***
Documentation     Does Lab even load?
Resource          ../_resources/Lab.robot
Test Setup        Wait for GTCOARLab to Open

*** Test Cases ***
Lab Opens
    [Documentation]    Did we break lab?
    Capture Page Screenshot    00-smoke.png
    Log    Looks Good!
