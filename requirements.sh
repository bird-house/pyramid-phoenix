#!/bin/bash

if [ -f /etc/debian_version ] ; then
    echo "Installing Debian/Ubuntu packages ..."
    #sudo apt-get -y install wget
    sudo apt-get -y install libldap2-dev libsasl2-dev python-all-dev # needed by pyramid_ldap
    # FK: The cleaner way would be to invoke 'sudo apt-get -y build-dep python-ldap'
    #     but source code repo's are likely to be disabled so that this one would fail.
    # TODO: Add these dependencies for the other platforms as well.
elif [ -f /etc/redhat-release ] ; then
    echo "Installing RedHat/CentOS packages ..."
    #sudo yum -y install wget
elif [ `uname -s` = "Darwin" ] ; then
    echo "Installing MacOSX/Homebrew packages ..."
    #brew install wget
fi
