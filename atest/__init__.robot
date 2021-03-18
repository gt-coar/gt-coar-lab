# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

*** Settings ***
Documentation     GTCOARLab
Library           OperatingSystem
Resource          ./_resources/Install.robot
Force Tags        gtcl:os:${OS}    gtcl:version:${VERSION}    gtcl:build:${BUILD}
...               gtcl:variant:${VARIANT}    gtcl:attempt:${ATTEMPT}
Suite Setup       Maybe Run the Installer
Suite Teardown    Clean up the Test
