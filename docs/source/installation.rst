.. _installation:

Installation
============

Start with downloading Phoenix with sources from github:

.. code-block:: console

   $ git clone https://github.com/bird-house/pyramid-phoenix.git
   $ cd pyramid-phoenix

Create the conda_ environment and activate it:

.. code-block:: console

  $ conda env create -f environment.yml
  $ conda activate pyramid-phoenix

Edit the configuration ``custom.cfg`` (see ``custom.cfg.example``). For example change the admin password:

.. code-block:: console

  $ vim custom.cfg
  # phoenix admin password
  phoenix-password = qwerty

When you're finished, run ``make install`` to install Phoenix into the conda environment.
The installation is using buildout_:

.. code-block:: console

   $ (pyramid-phoenix) make install

By default phoenix will be installed into the folder ``~/birdhouse``.

After successful installation you need to start the services:

.. code-block:: console

   $ (pyramid-phoenix) make start    # starts supervisor services
   $ (pyramid-phoenix) make status   # shows status of supervisor services

Phoenix web application is available on `http://localhost:8081`.

Check the log file for errors:

.. code-block:: console

   $ tail -f  ~/birdhouse/var/log/supervisor/phoenix.log
   $ tail -f  ~/birdhouse/var/log/supervisor/celery.log

.. _conda: https://conda.io/en/latest/
.. _buildout: http://www.buildout.org/en/latest/
