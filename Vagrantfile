# -*- mode: ruby -*-
# vi: set ft=ruby :

# This guide is optimized for Vagrant 1.7 and above.
Vagrant.require_version ">= 1.7.0"

Vagrant.configure("2") do |config|

#######################################
### phoenix Servers  ######################
#######################################

  # Disable the new default behavior introduced in Vagrant 1.7, to
  # ensure that all Vagrant machines will use the same SSH key pair.
  # See https://github.com/mitchellh/vagrant/issues/5005
  config.ssh.insert_key = false
  config.ssh.private_key_path = '~/.vagrant.d/insecure_private_key'

  config.vm.define "phoenix" do |phoenix|
    # phoenix.vm.box = "bento/ubuntu-18.04"
    # phoenix.vm.box = "bento/ubuntu-16.04"
    # phoenix.vm.box = "bento/debian-9"
    phoenix.vm.box = "bento/centos-7"
    # phoenix.vm.box = "bento/centos-6"
    # phoenix.vm.box = "bento/fedora-27"
    phoenix.vm.hostname = "phoenix.local"
    phoenix.vm.network "private_network", ip: "192.168.128.200"
  end
end
