Phoenix
=======

.. image:: https://travis-ci.org/bird-house/pyramid-phoenix.svg?branch=master
   :target: https://travis-ci.org/bird-house/pyramid-phoenix
   :alt: Travis Build


Phoenix (the bird)
  *Phoenix is a long-lived bird that is cyclically regenerated or reborn.* (`Wikipedia <https://en.wikipedia.org/wiki/Phoenix_%28mythology%29>`_). [..]

Pyramid Phoenix is a web-application build with the Python web-framework `Pyramid <http://www.pylonsproject.org/>`_. 
Phoenix makes it easy to interact with Web Processing Services (WPS).

For installation and configuration read the `documentation on ReadTheDocs <http://pyramid-phoenix.readthedocs.org/en/latest/index.html>`_.

Phoenix is part of the `Birdhouse <http://bird-house.github.io/>`_ project.

Run Docker
----------

Set the ``HOSTNAME`` environment variable (not ``localhost``) and run ``docker-compose``:

.. code-block:: sh

   HOSTNAME='myhost.earth' bash -c 'docker-compose up'

