#!/usr/bin/env bash
set -eux

df -h

systemctl stop snapd.service

snap remove chromium
snap remove gtk-common-themes
snap remove gnome-3-28-1804
snap remove lxd
snap remove core18
snap remove snapd

snap list --all | awk '/disabled/{print $1, $3}' |
    while read snapname revision; do
        snap remove "$snapname" --revision="$revision"
    done

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
