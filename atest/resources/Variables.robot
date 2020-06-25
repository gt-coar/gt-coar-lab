*** Settings ***
Documentation     Variables used in more than one places

*** Variables ***
${INSTALL LOG}    ${OUTPUT DIR}${/}00_installer.log
&{GECKODRIVER}    linux=bin${/}geckodriver    darwin=bin${/}geckodriver    windows=Scripts${/}geckodriver.exe
&{FIREFOX}        linux=bin${/}firefox    darwin=bin${/}firefox    windows=Library${/}bin${/}firefox.exe
