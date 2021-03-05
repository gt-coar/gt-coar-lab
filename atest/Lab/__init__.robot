# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License

*** Settings ***
Documentation     Actually test the Lab application
Resource          ../_resources/Lab.robot
Library           JupyterLibrary
Suite Setup       Start GTCOARLab
