*** Settings ***
Documentation     Keywords for running things in the Installation
Library           Process
Library           OperatingSystem

*** Variables ***
${NEXT CLI LOG}    ${0}

*** Keywords ***
Run Shell Script in Installation
    [Arguments]    ${cmd}    ${rc}=${0}
    [Documentation]    Run a command in the Installation environment
    ${logs} =    Set Variable    ${OUTPUT DIR}${/}cli
    Create Directory    ${logs}
    ${log} =    Set Variable    ${logs}${/}${NEXT CLI LOG}-${cmd.split()[0]}
    Set Global Variable    ${NEXT CLI LOG}    ${NEXT CLI LOG.__add__(1)}
    ${shell} =    Set Variable    ${ACTIVATE} && ${cmd}
    Create File    ${log}.args    ${shell}
    ${proc} =    Run Process    ${shell}
    ...    shell=True    cwd=${OUTPUT DIR}    stdout=${log}.log    stderr=STDOUT    env:PS1=[gtc]
    Should Be Equal As Numbers    ${proc.rc}    ${rc}
    ${output} =    Get File    ${log}.log
    [Return]    ${output}
