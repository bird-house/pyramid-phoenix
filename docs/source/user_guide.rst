.. _userguide:

User Guide
==========

The user guide explains how to use the Phoenix web application to interact with Web Processing Services.

.. contents::
    :local:
    :depth: 2

.. _login:

Login
-----

Press the ``Sign in`` button in the upper right corner.

.. image:: _images/signin.png
  :scale: 50%

The login page offers you several options to login to Phoenix.

.. image:: _images/login.png
  :scale: 50%

You can login using your ESGF OpenID or your GitHub account.
If you login for the first time your account needs to be activated by an administrator.

If you are Phoenix admin you can also enter the admin password here.

**ESGF OpenID**

You can use an `ESGF OpenID <https://www.earthsystemcog.org/projects/cog/tutorials_web>`_.
The ESGF OpenID is used later to access files from `ESGF <https://esgf.llnl.gov/>`_.
Make sure, that you have a valid ESGF OpenID of one of the ESGF Providers
(for example `DKRZ <http://esgf-data.dkrz.de/>`_)
and that you are able to download a datafile (you need to register for CMIP5 and CORDEX).

Enter the account name of your ESGF OpenID and choose the according
ESGF OpenID provider (by default this is DKRZ).

.. image:: _images/login_esgf.png
  :scale: 50%


Dashboard
---------

The dashboard shows some statistics about jobs and users.

.. image:: _images/dashboard.png

.. _processes:

Processes
---------

When you have registered WPS services you can run a process. Go to the
``Processes`` tab.

.. image:: _images/processes.png

Choose one of your registered WPS services. You will get a list of available processes (WPS ``GetCapabilities`` request).

.. image:: _images/processes_list.png

Choose one of these processes by using the ``Execute`` button.

.. _execute:

In case of Emu you may try the ``Hello World`` process. You will then be
prompted to enter your username:

.. image:: _images/processes_execute.png

Press the ``Submit`` button. When the process is submitted you will be shown your job list in ``Monitor``.

.. _myjobs:

Monitor
-------

In ``Monitor`` all your running or finished jobs are listed.
The list shows the status and progress of your jobs.

.. image:: _images/myjobs.png

When a job has finished with success you can see the results by clicking the ``Details`` button.

.. image:: _images/myjobs_details.png

If the result has a document (XML, text, NetCDF, ...) you can view or download this document with the ``Download`` button.

.. _myaccount:

My Account
----------

In ``My Account`` you can change your user settings (user name, organisation, openid, ...).

.. image:: _images/myaccount.png

You can also see your current `Twitcher`_ access token which you can use to access a registered WPS service directly.

.. image:: _images/twitcher-token.png

See the Twitcher :ref:`twitcher:tutorial` on how to use the token to access a WPS service.


Settings (admins only)
----------------------

When you are logged-in as admin user you have the ``Settings`` page. Here you can make administrative changes and monitor services.

.. image:: _images/settings.png

.. _register_wps:

Register a WPS service
~~~~~~~~~~~~~~~~~~~~~~

Open the ``Settings/Services`` page. Here you can see which services are registered in the catalog.
All theses services are known and usable by Phoenix.

.. image:: _images/settings_services.png

To add a new WPS service, press the ``Register a new Service`` button and enter the WPS URL in the field ``Service URL``.

For example, to register Emu WPS:

http://localhost:5000/wps

.. image:: _images/add_wps_service.png

.. _activate_users:

Activate Users
~~~~~~~~~~~~~~

Open the ``Settings/Users`` page. Here you activate/deactivate users and also remove them. When a user has registerd to the Phoenix web application the user needs to be activated before the user can login.

Choose Authentication Protocol
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open the ``Settings/Auth`` page. Here you can choose the different authentication protocols (OpenID, LDAP, ...) which users can use on the login page. ``Local Auth`` enables the local admin account whose password is set in ``custom.cfg`` in your Phoenix installation.

.. image:: _images/settings_auth.png


GitHub Support
~~~~~~~~~~~~~~

You can use GitHub accounts to login to Phoenix. GitHub uses OAuth2. First you need to register your Phoenix application at `GitHub <https://github.com/settings/applications/new>`_. Then go to ``Settings/GitHub`` in your Phoenix application and enter the ``GitHub Consumer Key/Client ID`` and ``GitHub Consumer Secret/Client Secret``:

.. image:: _images/settings_github.png
