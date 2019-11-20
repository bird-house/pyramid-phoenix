.. Phoenix documentation master file, created by
   sphinx-quickstart on Wed Mar 11 13:38:39 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _introduction:

Introduction
============

Phoenix (the bird)
  *Phoenix is a long-lived bird that is cyclically regenerated or reborn.* (`Wikipedia <https://en.wikipedia.org/wiki/Phoenix_%28mythology%29>`_). [..]

Pyramid Phoenix is a web-application build with the Python web-framework Pyramid_.
Phoenix has a user interface to interact with `Web Processing Services`_.
The user interface gives you the possibility to :ref:`register Web Processing Services <register_wps>`.
For these registered WPS services you can see which :ref:`processes` they have available.
You are provided with a form page to enter the parameters to :ref:`execute a process (job) <execute>`.
You can :ref:`monitor the jobs <myjobs>` and see the results.

Phoenix should help developers of WPS processes to use their processes more conveniently.
Phoenix is also used for demonstration of available WPS processes.

Phoenix is installed using the Conda_ Python distribution and Buildout_.

.. toctree::
   :maxdepth: 2

   installation
   configuration
   user_guide
   tutorial
   troubleshooting

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Conda: https://docs.conda.io/en/latest/
.. _Buildout: http://www.buildout.org/en/latest/
.. _Pyramid: https://trypyramid.com/
.. _Web Processing Services: https://www.opengeospatial.org/standards/wps
