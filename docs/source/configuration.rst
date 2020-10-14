.. _configuration:

Configuration
=============

You can configure Phoenix by editing ``custom.cfg`` in the Phoenix source folder:

.. code-block:: sh

   $ cd pyramid-phoenix
   $ vim custom.cfg
   $ cat custom.cfg

.. code-block:: ini

   [settings]
   hostname = localhost
   http-port = 8081
   https-port = 8443
   log-level = INFO
   # phoenix admin password
   phoenix-password = qwerty

By default Phoenix runs on localhost. The HTTP port 8081 is redirected to the HTTPS port 8443.
If you want to use a different hostname/port then edit the default values in ``custom.cfg``:

.. code-block:: ini

   [settings]
   hostname = localhost
   http-port = 8081
   https-port = 8443

To activate the GitHub login for external users you need to configure a GitHub application key for your Phoenix web application:

.. code-block:: ini

   [settings]
   # register at github: https://github.com/settings/applications/new
   github-consumer-key = ########################
   github-consumer-secret = ############################

See the `GitHub Settings`_ on how to generate the application key for Phoenix.

After any change to your ``custom.cfg`` you **need** to run ``make install`` again and restart the ``supervisor`` service:

.. code-block:: sh

  $ make install
  $ make restart

.. _GitHub Settings: https://github.com/settings/applications/new
