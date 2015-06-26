.. _installation:

Installation
============

This installation works on Linux 64-bit (Ubuntu 14.04, Centos 6, ...). It might still work on MacOSX but packages are updated only from time to time. Most of the dependencies come from :term:`birdhouse:Anaconda` Python distribution system. Additional conda packages come from the `Binstar channel Birdhouse <https://binstar.org/birdhouse>`_. The installation is done with :term:`birdhouse:Buildout`.

Phoenix uses WPS processes provided by Malleefowl. As a requiste you should install a local Malleefowl WPS (this will become part of the Phoenix installer). Alternatively you could configure the WPS URL of a running Malleefowl WPS instance in the Phoenix ``custom.cfg``.

To install Malleefowl follow the instructions given in the :ref:`Malleefowl documentation <malleefowl:installation>`. In short:

.. code-block:: sh

   $ git clone https://github.com/bird-house/malleefowl.git
   $ cd malleefowl
   $ make

Now start with installing Phoenix with sources from github:

.. code-block:: sh

   $ git clone https://github.com/bird-house/pyramid-phoenix.git
   $ cd pyramid-phoenix
   $ make

For other install options run ``make help`` and read the documention for the :ref:`Makefile <bootstrap:makefile>`.

After that you *need* to create a password for the local ``phoenix`` user which is used to login to the Phoenix web application:

.. code-block:: sh

   $ make passwd
   Generate Phoenix password ...
   Enter a password with at least 8 characters.
   Enter password: 
   Verify password:

   sha256:#############
   
   Add this password to custom.cfg: phoenix-password = ...
   Run 'make install restart' to activate this password.

Follow the instructions given and add the password hash as ``phoenix-password = sha256:###`` in ``custom.cfg``. After that run:

.. code-block:: sh

   $ make install
     
You always have to run ``make install`` after changes in custom.cfg. 

After successful installation you need to start the services. All installed files (config etc ...) are below the conda environment ``birdhouse`` which is by default in your home directory ``~/.conda/envs/birdhouse``. Now, start the services:

.. code-block:: sh

   $ make start    # starts supervisor services
   $ make status   # shows status of supervisor services

Phoenix web application is available on http://localhost:8081. 

Check the log file for errors:

.. code-block:: sh

   $ tail -f  ~/.conda/envs/birdhouse/var/log/supervisor/phoenix.log
   $ tail -f  ~/.conda/envs/birdhouse/var/log/supervisor/celery.log

