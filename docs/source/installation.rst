.. _installation:

Installation
============

This installation works on Linux 64-bit (Ubuntu 14.04, Centos 6, ...). It might still work on MacOSX but packages are updated only from time to time. Most of the dependencies come from :term:`Anaconda <birdhouse:anaconda>` Python distribution system. Additional conda packages come from the `Binstar channel Birdhouse <https://binstar.org/birdhouse>`_. The installation is done with :term:`Buildout <birdhouse:buildout>`.

Phoenix uses WPS processes provided by Malleefowl. As a requiste you should install a local Malleefowl WPS (this will become part of the Phoenix installer). Alternatively you could configure the WPS URL of a running Malleefowl WPS instance in the Phoenix ``custom.cfg``.

To install Malleefowl follow the instructions given in the :ref:`Malleefowl documentation <malleefowl:installation>`. In short::

   $ git clone https://github.com/bird-house/malleefowl.git
   $ cd malleefowl
   $ make

Now start with installing Phoenix with sources from github::

   $ git clone https://github.com/bird-house/pyramid-phoenix.git
   $ cd pyramid-phoenix
   $ make

For other install options run ``make help`` and read the documention for the :ref:`Makefile <bootstrap:makefile>`.

After successful installation you need to start the services. All installed files (config etc ...) are below the conda environment ``birdhouse`` which is by default in your home directory ``~/.conda/envs/birdhouse``. Now, start the services::

   $ make start    # starts supervisor services
   $ make status   # shows status of supervisor services

Phoenix web application is available on http://localhost:8081. You will need an OpenID to login to Phoenix. Admin users are configured in the ``custom.cfg`` file (see Configuration). Normal Users need to be registered on the ``Settings/User`` page. By default there is a local admin user (admin@malleefowl.org) with no OpenID. To login with this user open 

http://localhost:8081/login/local

The local admin user can be deactivated by removing it from the admin users list in ``custom.cfg``.

Check the log file for errors::

   $ tail -f  ~/.conda/envs/birdhouse/var/log/phoenix.log

