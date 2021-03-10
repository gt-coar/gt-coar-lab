#!/usr/bin/env bash
# Copyright (c) 2021 University System of Georgia and GTCOARLab Contributors
# Distributed under the terms of the BSD-3-Clause License
set -eux

df -h

systemctl stop snapd.service

for i in {1..10}; do
    echo "attempt ${i}..."
    snap remove chromium && break
    sleep 15
done

snap remove chromium
snap remove gtk-common-themes
snap remove gnome-3-28-1804
snap remove lxd
snap remove core18
snap remove snapd

# shellcheck disable=SC2162
snap list --all | awk '/disabled/{print $1, $3}' | while read snapname revision; do
    snap remove "$snapname" --revision="$revision"
done

# shellcheck disable=SC2035
sudo apt-get purge \
    r-* \
    php* \
    mono-* \
    mysql* \
    dotnet-* \
    mongodb* \
    *openjdk* \
    google-chrome*

apt-get -y autoclean
apt-get -y autoremove
apt-get -y clean

rm -rf \
    "/usr/local/share/boost" \
    "$AGENT_TOOLSDIRECTORY" \
    /var/lib/apt/lists/*

apt list --installed

df -h
