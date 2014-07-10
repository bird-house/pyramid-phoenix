#!/bin/bash
if [ -f /etc/debian_version ] ; then
    sudo apt-get -y --force-yes install wget build-essential
elif [ -f /etc/redhat-release ] ; then
    sudo yum -y install wget
elif [ `uname -s` = "Darwin" ] ; then
    brew install wget
fi
