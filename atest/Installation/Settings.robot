# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

*** Settings ***
Documentation     Did the install steps occur correctly?
Library           OperatingSystem
Library           Collections
Resource          ../_resources/JSON.robot

*** Test Cases ***
Overrides
    [Documentation]    Did post_install.(sh|bat) correctly update Lab overrides?
    ${path} =    Set Variable
    ...    ${INST_DIR}${/}share${/}jupyter${/}lab${/}settings${/}overrides.json
    File Should Exist    ${path}
    ${observed} =    Get File as JSON    ${path}
    ${expected} =    Get File as JSON    ${OVERRIDES}
    Dictionaries Should Be Equal    ${observed}    ${expected}
