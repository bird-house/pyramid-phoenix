.. _userguide:

User Guide
==========

The user guide explains how to use the Phoenix web application to interact with Web Processing Services.

Login
-----

You need an OpenID account to login to Phoenix. You should use a `ESGF OpenID <https://github.com/ESGF/esgf.github.io/wiki/ESGF_Data_Download>`_ which is used later to access files from ESGF.

Now, press the ``Sign in`` button in the upper right corner.

.. image:: _images/signin.png

Next you will have a page where you can enter the account name of you ESGF OpenID. Choose the according ESGF OpenID provider (by default this is DKRZ).

.. image:: _images/openid.png 


Dashboard
---------

The dashboard shows some statistics about jobs and users. Currently there is not that much to see.

.. image:: _images/dashboard.png

Processes
---------

When you have registered WPS services you can run a process. Go to the
``Processes`` tab and use the ``Choose WPS`` button to choose one of
your registered WPS servces. You will get a list of available
processes (WPS ``GetCapabilities`` request). Choose one of these
processes by using the ``Execute`` button. In case of Malleefowl you
may try the ``Logon with ESGF OpenID`` process. You will then be
prompted to enter your ESGF OpenID
(e.a. https://esgf-data.dkrz.de/esgf-idp/openid/myname) and
password. Press the ``Submit`` button. When the process is submitted
you will be shown your job list in ``My Jobs``. The list shows the
status and progress of your jobs. When a job has finished with success
you can see the results by using the ``Show`` button. In case of the
``Logon`` process you should have as output a link to your X509 proxy
certificate. You can open the link by pressing ``View``.


My Jobs
-------

Wizard
------

The wizard is used to chain WPS processes and to collect the input
parameters. Currently the wizard chains a user WPS process with a WPS
process to retrieve ESGF data. Go to the ``Wizard`` tab. Enter the
appropiate parameters and use ``Next`` to get to the next wizard
page. You need to choose a WPS service (e.a. Malleefowl), a process
(in case of Malleefowl only ``Dummy``), select the input parameter of
the choosen process (mime-type application/netcdf), select the input
source (ESGF), select an ESGF dataset (select categorie (blue) and
values of this category (orange), current selection (green)). Please
select **only one Dataset**! You might be prompted for your password
for your OpenID. On the final page you can enter some keywords for
your process and mark it as favorite (when using a favorite you don't
need to enter all parameters again). Press ``Done`` and the job will
be started and shown in your job list ``My Jobs``. When the job has
finished you can see the results by pressing ``View``. The input files
can be seen on the ``Resources`` tab. Also use ``View`` to open the
file list.


My Account
----------

In ``My Account`` you can change your user settings (user name, organisation, openid, ...).

.. image:: _images/myaccount.png

If you have a valid ESGF OpenID you can update your X509 credentials. This is a X509 proxy certificate which is used to access ESGF data. To update press the button ``Update Credentials`` and enter your OpenID password in the dialog.

.. image:: _images/update_creds.png

Settings (admins only)
----------------------

When you are logged-in as admin user you have the ``Settings`` page. Here you can make administrative changes and monitor services. 

.. image:: _images/settings.png

Register a WPS service
~~~~~~~~~~~~~~~~~~~~~~

Open the ``Settings/Catalog`` page. Here you can see which services are registered in the catalog service (we are using `PyCSW <http://pycsw.org/>`_). All theses services are known and useable by Phoenix.

.. image:: _images/catalog.png

To add a new WPS service press the ``Add Service`` button and enter the WPS URL in the field ``Service URL``, for example Malleefowl WPS:

http://localhost:8091/wps

.. image:: _images/add_service.png





