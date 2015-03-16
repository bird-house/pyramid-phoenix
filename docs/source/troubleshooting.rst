.. _troubleshooting:

Troubleshooting
===============

.. contents::
   :local:
   :depth: 2
   :backlinks: none

Phoenix does not start
----------------------

Phoenix needs a running mongodb and pycsw service. Sometimes Phoenix is started when these service are not ready yet (will be fixed soon). In that case start theses services manually in the order mongodb, pycsw and Phoenix with::

    $ source activate birdhouse     # activate conda birdhouse environment
    $ supervisorctl restart mongodb
    $ supervisorctl restart pycsw
    $ supervisorctl restart phoenix

You can also try to restart all services with::

    $ supervisorctl restart all

or::

    $ make restart
   
Nginx does not start
--------------------

From a former installation there might be nginx files with false permissions. Remove those files::

   $ ~/.conda/env/birdhouse/etc/init.d/supervisord stop
   $ sudo rm -rf ~/.conda/env/birdhouse/var/run
   $ sudo rm -rf ~/.conda/env/birdhouse/var/log
   $ ~/.conda/env/birdhouse/etc/init.d/supervisord start
   

