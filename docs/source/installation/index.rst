.. _installation:
************
Installation
************

.. _require:
===============
Prerequirements
===============
    
* Currently the buildout installation works *only on the 64 Bit version of Ubuntu 12.04* or above.
* Installing and running Birdhouse requires some resources. So you should *have a recent machine* (2 Cores, 4 GB).
* The buildout installation process will install required system packages. Therefore *you need sudo rights*. 

.. _malleefowl:
==========================
Installing Malleefowl (WPS service)
==========================

In the installation process you will be *asked for your password* to
run package installation with sudo rights.

For installing Malleefowl follow the next steps.::

1 - cd to installation folder::
        
        $ cd $HOME/sandbox

2 - checkout from git repo::

        $ git clone git://redmine.dkrz.de/malleefowl.git

3 - cd into the new folder malleefowl::

        $ cd malleefowl

4 - you should use the develop version to get recent updates::

        $ git checkout develop

4 - run install script::

        $ ./install.sh

5 - get yourself some tee or coffee. Be
prepared to enter your password for sudo because buildout will install
dependend packages with the system package manager (apt on
Debian/Ubuntu or yum on RedHat/CentOS).

.. _phoenix:
==========================
Installing Phoenix (WPS web client)
==========================

In the installation process you will be *asked for your password* to
run package installation with sudo rights.

For installing Phoenix follow the next steps.::

1 - cd to installation folder::
        
        $ cd $HOME/sandbox

2 - checkout from git repo::

        $ git clone git://redmine.dkrz.de/phoenix.git

3 - cd into the new folder phoenix::

        $ cd phoenix

4 - you should use the develop version to get recent updates::

        $ git checkout develop

4 - run install script::

        $ ./install.sh

5 - get yourself some tee or coffee. Be
prepared to enter your password for sudo because buildout will install
dependend packages with the system package manager (apt on
Debian/Ubuntu or yum on RedHat/CentOS).

7 - maybe restart phoenix/malleefowl services with supervisor::

        $ sudo supervisorctl
        > status
        > restart all

8 - open your browser and go the start page::

        $ firefox http://localhost:8090

9 - you need a mozilla persona account to sign-in::

     https://login.persona.org/about

10 - have fun :)

 
.. _starting:
=================
Starting Birdhouse
=================

The Birdhouse services are monitored with supervisor. Birdhouse uses
the `nginx` webserver which is installed during buildout installation.

First make sure that `nginx` is running (it is started automatically)::

       $ sudo /etc/init.d/nginx status

If nginx is not started then do it with::

       $ sudo /etc/init.d/nginx start

Check that supervisor is running::

       $ sudo /etc/init.d/supervsior status

and start supervisor if necessary.

Check the status of Birdhouse services with supervisor monitor::

       $ sudo supervisorctl

You get an interactive console and you can run commands like `status`, `restart all`, `stop all`.

.. _custom:
=================================
Customizing Installation Settings
=================================

If you need to change the default settings of the buildout
installation process then you must provide a custom configuration file
for buildout. This is for example *necessary* when climdaps is running
on a *remote server* and you can not access the services via
localhost. In this case do the following::

       $ cd $HOME/sandbox/phoenix
       $ vim custom.cfg

The content of your custom config might look like this::

       [buildout]

       extends = buildout.cfg

       [server]
       host = 192.168.0.10
       hostname = fastduck.lake.org


It is *import* that your custom configuration file extends the default
`buildout.cfg`. You can overwrite more options. For this you have to
check the buildout configuration files.

.. _update:
=========================
Get Updates from Git Repo
=========================

You can update your installation from the `git` repository::

        $ cd $HOME/sandbox/phoenix
        $ git pull

If you have local changes git might complain about it. If you *don't want to keep*
your changes do the following::

        $ git checkout -- .     # reverts to checkout git revision

If you want to *keep your changes* you might use the `git stash` command::

        $ git stash            # just move your changes into stash
        $ git help stash       # see further options

After you successfully got the current version of Birdhouse from `git` run buildout again::

        $ ./install.sh
        
Then restart your Birdhouse services with `supervisor`::

        $ sudo supervisorctl
        > status
        > restart all

See (starting Birdhouse) for further instructions.
