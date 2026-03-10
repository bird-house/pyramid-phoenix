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

The conda environment is intentionally minimal (bootstrap only). Application and
service dependencies are installed by buildout during ``make install``.

Bootstrap buildout in the active environment:

.. code-block:: console

   $ (pyramid-phoenix) make bootstrap

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

If a restart races with supervisor shutdown on your machine, use:

.. code-block:: console

   $ (pyramid-phoenix) make stop
   $ (pyramid-phoenix) make start

Phoenix web application is available on `http://localhost:8081`.

The default local nginx configuration uses HTTP only.

Check the log file for errors:

.. code-block:: console

   $ tail -f  ~/birdhouse/var/log/supervisor/phoenix.log
   $ tail -f  ~/birdhouse/var/log/supervisor/celery.log

Troubleshooting
---------------

Supervisor restart reports a port conflict:

.. code-block:: console

   $ (pyramid-phoenix) make stop
   $ pkill -f supervisord || true
   $ (pyramid-phoenix) make start

Services are not all ``RUNNING``:

.. code-block:: console

   $ (pyramid-phoenix) make status
   $ tail -f ~/birdhouse/var/log/supervisor/phoenix.log
   $ tail -f ~/birdhouse/var/log/supervisor/celery.log

Dependency drift or stale buildout artifacts:

.. code-block:: console

   $ (pyramid-phoenix) make clean
   $ (pyramid-phoenix) make install

.. _conda: https://conda.io/en/latest/
.. _buildout: http://www.buildout.org/en/latest/
