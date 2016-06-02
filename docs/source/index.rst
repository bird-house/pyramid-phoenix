.. Phoenix documentation master file, created by
   sphinx-quickstart on Wed Mar 11 13:38:39 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _introduction:

Introduction
============

Phoenix (the bird)
  *Phoenix is a long-lived bird that is cyclically regenerated or reborn.* (`Wikipedia <https://en.wikipedia.org/wiki/Phoenix_%28mythology%29>`_). [..]

Pyramid Phoenix is a web-application build with the Python web-framework :term:`birdhouse:pyramid`. 
Phoenix has a user interface to make it easier to interact with :term:`Web Processing Services <birdhouse:wps>`.
The user interface gives you the possibility to :ref:`register Web Processing Services <register_wps>`.
For these registered WPS services you can see which :ref:`processes` they have available. 
You are provided with a form page to enter the parameters to :ref:`execute a process (job) <execute>`.
You can :ref:`monitor the jobs <myjobs>` and see the results. 

In the climate science community many analyses are using climate data in the :term:`birdhouse:NetCDF` format.
Phoenix uses the `Malleefowl`_ WPS which provides processes to access NetCDF files from
the :term:`birdhouse:ESGF` data archive. Malleefowl provides a :term:`birdhouse:workflow` process to chain ESGF 
data retrieval with 
another WPS process which needs NetCDF data as input. Phoenix has a :ref:`wizard` to collect the parameters to run 
such a workflow with a process of a registered WPS. 

Phoenix should help developers of WPS processes to use their processes more conveniently, especially for feeding
their processes with different data sources (like ESGF data archive). Phoenix is also used for demonstration of 
available WPS processes. 

Phoenix has a more generic and technical user interface. To use Phoenix successfully you need to have some 
knowledge about WPS and the existing data archives. So, Phoenix might not become a good choice for 
scientists users who just want to run a specific analyses job. There are other climate portals available which address these users.
But Phoenix should at least become *developer friendly*. 

Phoenix is easy to install using the :term:`birdhouse:anaconda` python distribution and :term:`birdhouse:buildout`. 
So, Phoenix is not only available on production sites where it is close to data archives. You can also install it on your developer machine to make testing of your developed WPS processes easier and to present them to other people.   

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

