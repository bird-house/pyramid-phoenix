#!/bin/bash
BUILDOUT_DIR=`dirname $0`
ANACONDA_HOME=$HOME/anaconda
DOWNLOAD_CACHE=$BUILDOUT_DIR/downloads
ANACONDA_URL=http://repo.continuum.io/miniconda
FN_LINUX=Miniconda-latest-Linux-x86_64.sh
FN_OSX=Miniconda-3.5.5-MacOSX-x86_64.sh

function install_anaconda() {
    # run miniconda setup, install in ANACONDA_HOME
    if [ -d $ANACONDA_HOME ]; then
        echo "Anaconda already installed in $ANACONDA_HOME."
    else
        FN=$FN_LINUX
        if [ `uname -s` = "Darwin" ] ; then
            FN=$FN_OSX
        fi

        echo "Installing $FN ..."

        # download miniconda setup script to download cache with wget
        mkdir -p $DOWNLOAD_CACHE
        wget -q -c -O "$DOWNLOAD_CACHE/$FN" $ANACONDA_URL/$FN
        bash "$DOWNLOAD_CACHE/$FN" -b -p $ANACONDA_HOME   
    fi

    # add anaconda path to user .bashrc
    echo -n "Add \"$ANACONDA_HOME/bin\" to your PATH: "
    echo "\"export PATH=$ANACONDA_HOME/bin:\$PATH\""

    echo "Installing Anaconda ... Done"
}

install_anaconda

exit 0