#!/bin/bash

if [ -f /etc/debian_version ] ; then
    echo "Installing Debian/Ubuntu packages ..."
    sudo apt-get -y update
    #sudo apt-get -y install wget
    sudo apt-get -y install libldap2-dev libsasl2-dev python-all-dev # needed by pyramid_ldap
    # FK: The cleaner way would be to invoke 'sudo apt-get -y build-dep python-ldap'
    #     but source code repo's are likely to be disabled so that this one would fail.
elif [ -f /etc/redhat-release ] ; then
    echo "Installing RedHat/CentOS packages ..."
    #sudo yum -y install wget
    sudo yum -y install yum-utils
    sudo yum-builddep -y python-ldap
elif [ `uname -s` = "Darwin" ] ; then
    echo "Installing MacOSX/Homebrew packages ..."
    #brew install wget
    # TODO: Add pyramid_ldap dependencies for this platform.
fi
