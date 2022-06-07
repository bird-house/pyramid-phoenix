#!/usr/bin/env bash

sudo apt-get update
sudo apt install make

mkdir Downloads
cd Downloads

# install anaconda
echo "installing miniconda"
wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b

echo "setting up conda default python"
echo "export PATH=/home/vagrant/miniconda3/bin:$PATH" >> /home/vagrant/.bashrc