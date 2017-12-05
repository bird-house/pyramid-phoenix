.. _tutorial_cdoopendap:

Run CDO ensemble operation on CORDEX data from ESGF using OpenDAP
=================================================================

First you need to login. Please follow the login instructions in the :ref:`user guide <login>`.

.. contents::
   :local:
   :depth: 2
   :backlinks: none

Search and select CORDEX ensembles
----------------------------------

**Activate ESGF Search**

.. image:: ../_images/tutorial/ensmean_opendap_esgfsearch.png
  :scale: 50%

**Update ESGF credentials if asked**

.. image:: ../_images/tutorial/ensmean_opendap_esgf_logon.png
  :scale: 50%

**Search CORDEX Ensemble**

.. image:: ../_images/tutorial/ensmean_opendap_datasets.png

**Select Files (OpenDAP)**

.. image:: ../_images/tutorial/ensmean_opendap_files.png

Check the selected files in Cart (optional)
-------------------------------------------

.. image:: ../_images/tutorial/ensmean_opendap_cart.png
  :scale: 50%

.. image:: ../_images/tutorial/ensmean_opendap_cart_selection.png

Select Hummingbird WPS Service
------------------------------

Choose the Hummingbird WPS service which has CDO processes.

.. image:: ../_images/tutorial/ensmean_opendap_hummingbird.png

Choose "CDO Ensembles Operation" Process
----------------------------------------

.. image:: ../_images/tutorial/ensmean_opendap_process.png

Choose CDO ensmean Operator and OpenDAP datasets
------------------------------------------------

.. image:: ../_images/tutorial/ensmean_opendap_inputs.png

Monitor running Job
-------------------

The job is now submitted and can be monitored on the *Monitor* page:

.. image:: ../_images/tutorial/ensmean_opendap_monitor.png

Display the outputs
-------------------

Click on the ``Details`` button to get to the result of the submitted process.

**Outputs**

.. image:: ../_images/tutorial/ensmean_opendap_details.png

**Map**

.. image:: ../_images/tutorial/ensmean_opendap_map.png
