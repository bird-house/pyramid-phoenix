Phoenix
=======

Phoenix (the bird)
  *Phoenix is a long-lived bird that is cyclically regenerated or reborn.* (`Wikipedia https://en.wikipedia.org/wiki/Phoenix_%28mythology%29`_). [..]

Pyramid Phoenix is a web-application build with the Python web-framework `Pyramid http://www.pylonsproject.org/`_. Phoenix makes it easy to interact with Web Processing Services (WPS).

Installation
------------

Check out code from the phoenix git repo (will be available on github). Then do the following::

   $ cd pyramid-phoenix
   $ ./requirements.sh
   $ ./install.sh


After successful installation you need to start the services. Phoenix is using `Anaconda http://www.continuum.io/`_ Python distribution system. All installed files (config etc ...) are below the anaconda root folder which is by default in your home directory ``~/anaconda``. Now, start the services::

   $ cd ~/anaconda
   $ etc/init.d/supervisor start
   $ etc/init.d/nginx start

Phoenix web application is available on http://localhost:8081. You will need an OpenID to login to Phoenix.

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


Authors
-------

* `DKRZ http://www.dkrz.de`_
* `Climate Service Center http://www.climate-service-center.de/`_
* `IPSL http://www.ipsl.fr/`_



