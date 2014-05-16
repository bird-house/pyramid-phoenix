.. _phoenix:
Phoenix WPS Web Interface
=========================

Login
-----

You need a `Mozilla Persona`_ account to login to Phoenix.

If you want to give access to someone with a Mozilla Persona ID for your
Phoenix instance you must add the Persona ID (email Address) to the
whitelist of the Phoenix configuration file. For this edit the
Phoenix configuration file:

.. code-block:: bash
            
        $ cd $HOME/sandbox/climdaps/parts/phoenix
        $ vim phoenix.ini
        $ cat phoenix.ini
        phoenix.login.whitelist = tux@linux.org, pingu@antarctica.org

Currently a login is only necessary for the Admin and Monitor tab in Phoenix.

Admin
-----

On the tab you can delete the Phoenix database ... the whole Phoenix
database ... don't worry about it ;)

Monitor
-------

On this tab you can see if all Climdaps services are running. You can
also restart Phoenix (in case of config change) and PyWPS (in case of
changes to the WPS processes).

Future
------

This will all change in future ...

 
.. _`Mozilla Persona`: https://login.persona.org/
