Phoenix
=======

Phoenix (the bird)
  *Phoenix is a long-lived bird that is cyclically regenerated or reborn.* (`Wikipedia <https://en.wikipedia.org/wiki/Phoenix_%28mythology%29>`_). [..]

Pyramid Phoenix is a web-application build with the Python web-framework `Pyramid <http://www.pylonsproject.org/>`_. Phoenix makes it easy to interact with Web Processing Services (WPS).

Installation
------------

Phoenix uses WPS processes provided by Malleefowl. As a requiste you should install a local Malleefowl WPS (this will become part of the Phoenix installer). Alternatively you could configure the WPS URL of a running Malleefowl WPS instance in the Phoenix ``custom.cfg``.

To install Malleefowl follow the instructions given in the Malleefowl `Readme <https://github.com/bird-house/malleefowl/blob/master/README.rst>`_. In short::

   $ git clone https://github.com/bird-house/malleefowl.git
   $ cd malleefowl
   $ make

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

Register WPS services
---------------------

When Phoenix is started and you are logged-in as admin user you can register WPS services in ``Settings/Catalog``:

http://localhost:8081/settings/catalog 

Use the ``Add Service`` button and enter the WPS url as ``Service URL``, for example Malleefowl WPS:

http://localhost:8091/wps

Run a WPS Process
-----------------

When you have registered WPS services you can run a process. Go to the ``Processes`` tab and use the ``Choose WPS`` button to choose one of your registered WPS servces. You will get a list of available processes (WPS ``GetCapabilities`` request). Choose one of these processes by using the ``Execute`` button. In case of Malleefowl you may try the ``Logon with ESGF OpenID`` process. You will then be prompted to enter your ESGF OpenID (e.a. https://esgf-data.dkrz.de/esgf-idp/openid/myname) and password. Press the ``Submit`` button. When the process is submitted you will be shown your job list in ``My Jobs``. The list shows the status and progress of your jobs. When a job has finished with success you can see the results by using the ``Show`` button. In case of the ``Logon`` process you should have as output a link to your X509 proxy certificate. You can open the link by pressing ``View``.

Using the Wizard
----------------

The wizard is used to chain WPS processes and to collect the input parameters. Currently the wizard chains a user WPS process with a WPS process to retrieve ESGF data. Go to the ``Wizard`` tab. Enter the appropiate parameters and use ``Next`` to get to the next wizard page. You need to choose a WPS service (e.a. Malleefowl), a process (in case of Malleefowl only ``Dummy``), select the input parameter of the choosen process (mime-type application/netcdf), select the input source (ESGF), select an ESGF dataset (select categorie (blue) and values of this category (orange), current selection (green)). Please select **only one Dataset**! You might be prompted for your password for your OpenID. On the final page you can enter some keywords for your process and mark it as favorite (when using a favorite you don't need to enter all parameters again). Press ``Done`` and the job will be started and shown in your job list ``My Jobs``. When the job has finished you can see the results by pressing ``View``. The input files can be seen on the ``Resources`` tab. Also use ``View`` to open the file list.


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
   




