.. _tutorial_solrsearch: 

Use the Birdhouse Solr Search in the Wizard
===========================================

First you need to login. Please follow the login instructions in the :ref:`user guide <login>`.

.. contents::
   :local:
   :depth: 2
   :backlinks: none

Prepare Solr Search (Admins only)
---------------------------------

Register a thredds catalog in ``Settings/Services``. For example use:

http://www.esrl.noaa.gov/psd/thredds/catalog/Datasets/ncep.reanalysis2.dailyavgs/catalog.html

Index this Thredds Catalog in ``Settings/Solr``. 


Use the Wizard
--------------

.. image:: ../_images/tutorial/wizard.png 


Select Hummingbird WPS Service
------------------------------

For this example choose the Hummingbird WPS service which has CDO processes.

.. image:: ../_images/tutorial/ci_hummingbird.png 

Choose "CDO sinfo" Process
--------------------------

.. image:: ../_images/tutorial/ci_process.png

Choose Input Parameter
----------------------

.. image:: ../_images/tutorial/ci_input.png

Choose Birdhouse Solr as Source
------------------------

.. image:: ../_images/tutorial/solr_source.png


Choose Data from Solr Search
------------------------

.. image:: ../_images/tutorial/solr_search.png

Start Process
------------------------

.. image:: ../_images/tutorial/ci_done.png


Monitor running Job
-------------------

The job is now submitted and can be monitored on the *Monitor* page: 

.. image:: ../_images/tutorial/ci_monitor.png

Display the outputs
-------------------

Click on the Job ID link to get to the result of the submitted process.

**Job Log**

.. image:: ../_images/tutorial/solr_log.png


**Job Outputs**

.. image:: ../_images/tutorial/solr_outputs.png








