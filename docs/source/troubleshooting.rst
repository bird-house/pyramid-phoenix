.. _troubleshooting:

Troubleshooting
===============

#. Phoenix does not start

Phoenix needs a running mongodb and pycsw service. Sometimes Phoenix is started when these service are not ready yet (will be fixed soon). In that case start theses services manually in the order mongodb, pycsw and Phoenix with::

    $ ~/anaconda/bin/supervisorctl restart mongodb
    $ ~/anaconda/bin/supervisorctl restart pycsw
    $ ~/anaconda/bin/supervisorctl restart phoenix

You can also try to restart all services with::

    $ ~/anaconda/bin/supervisorctl restart all

or::

    $ make restart
   
#. Nginx does not start

From a former installation there might be nginx files with false permissions. Remove those files::

   $ ~/anaconda/etc/init.d/supervisord stop
   $ sudo rm -rf ~/anaconda/var/run
   $ sudo rm -rf ~/anaconda/var/log
   $ ~/anaconda/etc/init.d/supervisord start
   

