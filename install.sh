#!/bin/bash
PWD=`pwd`
BUILDOUT_DIR=`dirname $0`
DOWNLOAD_CACHE=downloads
ANACONDA_HOME="/opt/anaconda"
ANACONDA_FILE=Miniconda-2.2.2-Linux-x86_64.sh
ANACONDA_URL=http://repo.continuum.io/miniconda/$ANACONDA_FILE
ANACONDA_MD5=a24a8baa264dee7cfd9286ae3d4add60

# actions before build
function pre_build() {
    upgrade
    setup_cfg
    setup_os
    install_anaconda
}

# upgrade stuff which can not be done by buildout
function upgrade() {
    echo "Upgrading Phoenix ..."
}

# set configurion file for buildout
function setup_cfg() {
    if [ ! -d $DOWNLOAD_CACHE ]; then
        echo "Creating buildout downloads cache $DOWNLOAD_CACHE."
        mkdir -p $DOWNLOAD_CACHE
    fi

    if [ ! -f custom.cfg ]; then
        echo "Copy default configuration to $BUILDOUT_DIR/custom.cfg"
        cp custom.cfg.example custom.cfg
    else
        echo "Using custom configuration $BUILDOUT_DIR/custom.cfg"
    fi
}

# install os packages needed for bootstrap
function setup_os() {
    if [ -f /etc/debian_version ] ; then
        setup_debian
    fi
}

function setup_debian() {
    sudo apt-get -y --force-yes install wget subversion
}

function install_anaconda() {
    # download miniconda setup script to download cache with wget
    wget -q -c -O $DOWNLOAD_CACHE/$ANACONDA_FILE $ANACONDA_URL

    # md5 check sum on the current file you downloaded and save results to 'test1'
    test_md5=`md5sum "$DOWNLOAD_CACHE/$ANACONDA_FILE" | awk '{print $1}'`;
    if [ "$test_md5" != $ANACONDA_MD5 ]; then 
        echo "checksum didn't match!"
        echo "Installing Anaconda ... Failed"
        exit 1
    fi

    # run miniconda setup, install in ANACONDA_HOME
    if [ ! -d $ANACONDA_HOME ]; then
        sudo bash "$DOWNLOAD_CACHE/$ANACONDA_FILE" -b -p $ANACONDA_HOME
         # add anaconda path to user .bashrc
        #echo -e "\n# Anaconda PATH added by climdaps installer" >> $HOME/.bashrc
        #echo "export PATH=$ANACONDA_HOME/bin:\$PATH" >> $HOME/.bashrc
    fi

    # add anaconda to system path for all users
    #echo "export PATH=$ANACONDA_HOME/bin:\$PATH" | sudo tee /etc/profile.d/anaconda.sh > /dev/null
    # source the anaconda settings
    #. /etc/profile.d/anaconda.sh

    echo "Installing Anaconda ... Done"
}

# run install
function install() {
    echo "Installing Phoenix ..."
    echo "BUILDOUT_DIR=$BUILDOUT_DIR"
    echo "DOWNLOAD_CACHE=$DOWNLOAD_CACHE"

    cd $BUILDOUT_DIR
    
    pre_build
    $ANACONDA_HOME/bin/python bootstrap.py -c custom.cfg
    echo "Bootstrap ... Done"
    bin/buildout -c custom.cfg

    cd $PWD

    echo "Installing Phoenix ... Done"
}

function usage() {
    echo "Usage: $0"
    exit 1
}

install
