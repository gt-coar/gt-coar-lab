*** Settings ***
Documentation     Basic tests of GTCOARLab installer
Library           OperatingSystem
Resource          ./resources/Install.robot
Force Tags        os:${OS}    version:${VERSION}    build:${BUILD}
...               variant:${VARIANT}    attempt:${ATTEMPT}
Suite Setup       Maybe Run the Installer
