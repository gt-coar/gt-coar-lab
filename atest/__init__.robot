*** Settings ***
Documentation     Basic tests of GTCOARLab installer
Library           OperatingSystem
Resource          ./resources/Install.robot
Force Tags        os:${OS}    version:${VERSION}
Suite Setup       Run the Installer
Suite Teardown    Clean up the Installation
