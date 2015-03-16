.. _configuration:

Configuration
=============

To be able to login to Phoenix as admin you need to edit the ``custom.cfg`` in the Phoenix source folder::

   $ cd pyramid-phoenix
   $ vim custom.cfg
   $ cat custom.cfg
   [settings]
   hostname = localhost
   http-port = 8081
   admin-users = admin@malleefowl.org pingu@antartica.earth

Add your email of your OpenID account to the ``admin-users`` (space separated).

If you want to run on a different hostname or port then change the default values in ``custom.cfg``. 

After any change to your ``custom.cfg`` you **need** to run ``make install`` again and restart the ``supervisor`` service::

  $ make install
  $ make restart
