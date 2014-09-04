Phoenix
=======

Phoenix (the bird)
  *Phoenix is a long-lived bird that is cyclically regenerated or reborn.* (`Wikipedia https://en.wikipedia.org/wiki/Phoenix_%28mythology%29`_). [..]

Pyramid Phoenix is a web-application build with the Python web-framework `Pyramid http://www.pylonsproject.org/`_. Phoenix makes it easy to interact with Web Processing Services (WPS).

Installation
------------

Check out code from the phoenix github repo and start the installation::

   $ git clone https://github.com/bird-house/pyramid-phoenix.git
   $ cd pyramid-phoenix
   $ ./requirements.sh
   $ ./install.sh


After successful installation you need to start the services. Phoenix is using `Anaconda http://www.continuum.io/`_ Python distribution system. All installed files (config etc ...) are below the anaconda root folder which is by default in your home directory ``~/anaconda``. Now, start the services::

   $ cd ~/anaconda
   $ etc/init.d/supervisor start
   $ etc/init.d/nginx start

Phoenix web application is available on http://localhost:8081. You will need an OpenID to login to Phoenix.

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

After any change to your ``custom.cfg`` you **need** to run ``install.sh`` again and restart the ``supervisor`` service::

  $ ./install.sh
  $  ~/anaconda/etc/init.d/supervisor restart


Update
------

When updating your installation you should run ``clean.sh`` to remove outdated Python dependencies::

   $ cd pyramid-phoenix
   $ git pull
   $ ./clean.sh
   $ ./requirement.sh
   $ ./install.sh

And then restart the ``supervisor`` and ``nginx`` service.

You can also use the supervisor monitor on http://localhost:9001 to start services.

Troubleshooting
---------------

Phoenix needs a running mongodb and pycsw service. Sometimes Phoenix is started when these service are not ready yet (will be fixed soon). In that case start theses services manually in the order mongodb, pycsw and Phoenix with::

    $ ~/anaconda/etc/init.d/supervisor restart mongodb
    $ ~/anaconda/etc/init.d/supervisor restart pycsw
    $ ~/anaconda/etc/init.d/supervisor restart phoenix
   

Authors
-------

* `DKRZ http://www.dkrz.de`_
* `Climate Service Center http://www.climate-service-center.de/`_
* `IPSL http://www.ipsl.fr/`_



