Phoenix
=======

Phoenix (the bird)
  *Phoenix is a long-lived bird that is cyclically regenerated or reborn.* (`Wikipedia <https://en.wikipedia.org/wiki/Phoenix_%28mythology%29>`_). [..]

Pyramid Phoenix is a web-application build with the Python web-framework `Pyramid <http://www.pylonsproject.org/>`_. Phoenix makes it easy to interact with Web Processing Services (WPS).

Installation
------------

Phoenix uses WPS processes provided by Malleefowl. As a requiste you should install a local Malleefowl WPS (this will become part of the Phoenix installer). Alternatively you could configure the WPS URL of a running Malleefowl WPS instance in the Phoenix ``custom.cfg``.

To install Malleefowl follow the instructions given in the Malleefowl `Readme <https://github.com/bird-house/malleefowl/blob/master/README.rst>`_.

Now start with installing Phoenix with sources from github::

   $ git clone https://github.com/bird-house/pyramid-phoenix.git
   $ cd pyramid-phoenix
   $ make

For other install options run ``make help`` and read the documention for the `Makefile <https://github.com/bird-house/birdhousebuilder.bootstrap/blob/master/README.rst>`_.


After successful installation you need to start the services. Phoenix is using `Anaconda <http://www.continuum.io/>`_ Python distribution system. All installed files (config etc ...) are below the anaconda root folder which is by default in your home directory ``~/anaconda``. Now, start the services::

   $ make start    # starts supervisor services
   $ make status   # shows status of supervisor services

Phoenix web application is available on http://localhost:8081. You will need an OpenID to login to Phoenix. Admin users are configured in the ``custom.cfg`` file (see Configuration). Normal Users need to be registered on the Settings/User page. By default there is a local admin user (admin@malleefowl.org) with no OpenID. To login with this user open 

http://localhost:8081/login/local

The local admin user can be deactivated by removing it from the admin users list in ``custom.cfg``.

Check the log file for errors::

   $ tail -f  ~/anaconda/var/log/phoenix.log

Configuration
-------------

To be able to login to Phoenix as admin you need to edit the ``custom.cfg`` in the Phoenix source folder::

   $ cd pyramid-phoenix
   $ vim custom.cfg
   $ cat custom.cfg
   [settings]
   hostname = localhost
   http-port = 8081
   admin-users = admin@malleefowl.org

Add your email of your OpenID account to the ``admin-users`` (space seperated).

If you want to run on a different hostname or port then change the default values in ``custom.cfg``. 

After any change to your ``custom.cfg`` you **need** to run ``make install`` again and restart the ``supervisor`` service::

  $ make install
  $ make restart


Troubleshooting
---------------

Phoenix does not start:

Phoenix needs a running mongodb and pycsw service. Sometimes Phoenix is started when these service are not ready yet (will be fixed soon). In that case start theses services manually in the order mongodb, pycsw and Phoenix with::

    $ ~/anaconda/bin/supervisorctl restart mongodb
    $ ~/anaconda/bin/supervisorctl restart pycsw
    $ ~/anaconda/bin/supervisorctl restart phoenix

You can also try to restart all services with::

    $ ~/anaconda/bin/supervisorctl restart all

or::

    $ make restart
   

Nginx does not start:

From a former installation there might be nginx files with false permissions. Remove those files::

   $ ~/anaconda/etc/init.d/supervisord stop
   $ sudo rm -rf ~/anaconda/var/run
   $ sudo rm -rf ~/anaconda/var/log
   $ ~/anaconda/etc/init.d/supervisord start
   




