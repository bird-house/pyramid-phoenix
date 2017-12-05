.. _tutorial_cdoensemble:

Run CDO ensemble operation on CMIP5 data from ESGF
==================================================

First you need to login. Please follow the login instructions in the :ref:`user guide <login>`.

.. contents::
   :local:
   :depth: 2
   :backlinks: none

Use the Wizard
--------------

.. image:: ../_images/tutorial/wizard.png


Select Hummingbird WPS Service
------------------------------

For this example choose the Hummingbird WPS service which has CDO processes.

.. image:: ../_images/tutorial/ensmean_hummingbird.png

Choose "CDO Ensembles Operation" Process
----------------------------------------

.. image:: ../_images/tutorial/ensmean_process.png

Choose CDO ensmean Operator
---------------------------

.. image:: ../_images/tutorial/ensmean_operator.png
  :scale: 50%

Choose Input Parameter
----------------------

.. image:: ../_images/tutorial/ensmean_input.png
  :scale: 50%

Choose ESGF as Source
------------------------

.. image:: ../_images/tutorial/ensmean_source.png
  :scale: 50%

Update your ESGF credentials if asked
-------------------------------------

.. image:: ../_images/tutorial/ensmean_update_creds.png
  :scale: 50%

.. image:: ../_images/tutorial/ensmean_esgf_logon.png
  :scale: 50%

.. image:: ../_images/tutorial/ensmean_esgf_success.png
  :scale: 50%


Select ensembles of CMIP5 experiment
------------------------------------

.. image:: ../_images/tutorial/ensmean_esgf_cmip5_search.png


Start Process
------------------------

.. image:: ../_images/tutorial/ensmean_done.png
  :scale: 50%


Monitor running Job
-------------------

The job is now submitted and can be monitored on the *Monitor* page:

.. image:: ../_images/tutorial/ensmean_monitor.png

Display the outputs
-------------------

Click on the ``Details`` button to get to the result of the submitted process.

**Outputs**

.. image:: ../_images/tutorial/ensmean_details.png

**Map**

.. image:: ../_images/tutorial/ensmean_map.png
