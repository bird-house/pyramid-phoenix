#!/bin/bash
PWD=`pwd`
BUILDOUT_DIR=`dirname $0`
ANACONDA_HOME=$HOME/anaconda
HOMEBREW_HOME=/opt/homebrew
DOWNLOAD_CACHE=downloads
ANACONDA_FILE=Miniconda-latest-Linux-x86_64.sh
ANACONDA_URL=http://repo.continuum.io/miniconda/$ANACONDA_FILE
#ANACONDA_MD5=

# actions before build
function pre_build() {
    clean_build
    upgrade
    setup_cfg
    setup_os
    #install_homebrew
    install_anaconda
}

function clean_build() {
    echo "Cleaning buildout ..."
    rm -rf $BUILDOUT_DIR/downloads
    rm -rf $BUILDOUT_DIR/eggs
    rm -rf $BUILDOUT_DIR/develop-eggs
    rm -rf $BUILDOUT_DIR/parts
    rm -rf $BUILDOUT_DIR/bin
    rm -f $BUILDOUT_DIR/.installed.cfg
    rm -rf $BUILDOUT_DIR/*.egg-info
    echo "Cleaning buildout ... Done"
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
    elif [ -f /etc/redhat-release ] ; then
        setup_redhat
    fi
}

function setup_debian() {
    sudo apt-get -y --force-yes install wget build-essential
}

function setup_redhat() {
    sudo yum -y install wget
}

function install_anaconda() {
    # download miniconda setup script to download cache with wget
    wget -q -c -O $DOWNLOAD_CACHE/$ANACONDA_FILE $ANACONDA_URL

    # md5 check sum on the current file you downloaded and save results to 'test1'
    #test_md5=`md5sum "$DOWNLOAD_CACHE/$ANACONDA_FILE" | awk '{print $1}'`;
    #if [ "$test_md5" != $ANACONDA_MD5 ]; then 
    #    echo "checksum didn't match!"
    #    echo "Installing Anaconda ... Failed"
    #    exit 1
    #fi

    # run miniconda setup, install in ANACONDA_HOME
    if [ ! -d $ANACONDA_HOME ]; then
        sudo bash "$DOWNLOAD_CACHE/$ANACONDA_FILE" -b -p $ANACONDA_HOME

         # add anaconda path to user .bashrc
        #echo -e "\n# Anaconda PATH added by climdaps installer" >> $HOME/.bashrc
        #echo "export PATH=$ANACONDA_HOME/bin:\$PATH" >> $HOME/.bashrc
    fi

    sudo chown -R $USER $ANACONDA_HOME

    echo "Installing Anaconda ... Done"
}

function install_homebrew() {
    # see https://github.com/Homebrew/linuxbrew
    
    if [ -f /etc/debian_version ] ; then
        sudo apt-get -y --force-yes install build-essential curl git m4 ruby texinfo libbz2-dev libcurl4-openssl-dev libexpat-dev libncurses-dev zlib1g-dev
    fi

    if [ -f /etc/redhat-release ] ; then
        sudo yum -y groupinstall 'Development Tools' && sudo yum -y install curl git m4 ruby texinfo bzip2-devel curl-devel expat-devel ncurses-devel zlib-devel
    fi

    if [ ! -e $HOMEBRE_HOME ]; then
        echo "Installing Homebrew ..."
        ruby -e "$(wget -O- https://raw.github.com/Homebrew/linuxbrew/go/install)"
        sudo ln -sf $HOME/.linuxbrew $HOMEBREW_HOME
    fi
    echo "Installing Homebrew ... Done"
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
