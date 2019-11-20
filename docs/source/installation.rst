.. _installation:

Installation
============

The installation is done with :term:`birdhouse:Buildout`.
Most of the dependencies come from :term:`birdhouse:Anaconda` Python distribution system.

Start with downloading Phoenix with sources from github:

.. code-block:: console

   $ git clone https://github.com/bird-house/pyramid-phoenix.git
   $ cd pyramid-phoenix

For install options run ``make help``.

Before installation you *need* to create a password for the local ``phoenix`` user which is used to login to the Phoenix web application:

.. code-block:: console

   $ make passwd
   Generate Phoenix password ...
   Enter a password with at least 8 characters.
   Enter password:
   Verify password:

   Run 'make install restart' to activate this password.

Optionally take a look at ``custom.cfg`` and make additional changes. When you're finished, run ``make clean install`` to install Phoenix:

.. code-block:: console

   $ make clean install

You always have to rerun ``make update`` after making changes in custom.cfg.

After successful installation you need to start the services. All installed files (config etc ...) are below the conda environment ``birdhouse`` which is by default in your home directory ``~/.conda/envs/birdhouse``. Now, start the services:

.. code-block:: console

   $ make start    # starts supervisor services
   $ make status   # shows status of supervisor services

Phoenix web application is available on `http://localhost:8081`.

Check the log file for errors:

.. code-block:: console

   $ tail -f  ~/birdhouse/var/log/supervisor/phoenix.log
   $ tail -f  ~/birdhouse/var/log/supervisor/celery.log
