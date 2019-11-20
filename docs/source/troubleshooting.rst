.. _troubleshooting:

Troubleshooting
===============

.. contents::
   :local:
   :depth: 2
   :backlinks: none

Phoenix does not start
----------------------

Phoenix needs a running mongodb and pycsw service. Sometimes Phoenix is started when these service are not ready yet. In that case start theses services manually in the order mongodb, pycsw and Phoenix with:

.. code-block:: sh

    $ source activate pyramid-phoenix     # activate conda environment used by phoenix
    $ supervisorctl restart mongodb
    $ supervisorctl restart phoenix

You can also try to restart all services with:

.. code-block:: sh

    $ supervisorctl restart all

or:

.. code-block:: sh

    $ make restart

Check the log files to see the error messages:

.. code-block:: sh

   $ tail -f  ~/birdhouse/var/log/supervisor/phoenix.log
   $ tail -f  ~/birdhouse/var/log/supervisor/celery.log


Nginx does not start
--------------------

From a former installation there might be nginx files with false permissions. Remove those files:

.. code-block:: sh

   $ ~/birdhouse/etc/init.d/supervisord stop
   $ sudo rm -rf ~/birdhouse/var/run
   $ sudo rm -rf ~/birdhouse/var/log
   $ ~/birdhouse/etc/init.d/supervisord start
