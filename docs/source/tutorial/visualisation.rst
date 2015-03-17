.. _tutorial_timeseries_plot: 

Creating a timeseries plot
==========================

First you need to login. Please follow the login instructions in the :ref:`user guide <login>`.

Once the login procedure is done, processes are operable and data search and download within the ESGF data archive is possible. 
There are two ways to submit a process: *Processes* or *Wizard*

While with *Processes* you can select single operational processes the *Wizard* is guiding you through the necessary steps to submit a job. For getting an idea of the operation procedure choose the *Wizard* tab: 

.. image:: ../_images/wizard.png

The following steps are necessary to submit a job: 

.. contents::
   :local:
   :depth: 2
   :backlinks: none


Select WPS Service
------------------

For this example choose the Flyingpigeon WPS service which has process for the climate impact community.

.. image:: ../_images/tutorial/choose_flyingpigeon.png 

Choose Process
--------------

With clicking on *Next* you'll find the list of available processes. 
Check the **Visualisation of NetCDF files**.

.. image:: ../_images/tutorial/choose_visualisation.png

Enter Process Parameters
------------------------

Click on *Next* which guides you to the process parameter: 

.. image:: ../_images/tutorial/visualisation_params.png

The values in the data files are stored with defined varable names. Here are the most common ones: 

* tas -- mean air temperaure at 2m (in Kelvin)
* tasmin -- minimum air temperaure at 2m (in Kelvin)  
* tasmax -- maximum air temperaure at 2m (in Kelvin)
* pr -- pricipitation fulx at surface (in kg/second)
* ps -- air pressure at surface
* huss -- specific humidiy (in Kg/Kg)

A list of available variable names used for CMPI5 and CORDEX experiment can be found here in the Appendix B of this document: http://cordex.dmi.dk/joomla/images/CORDEX/cordex_archive_specifications.pdf . 

Select Data Source
------------------

In the next step you will choose the data source. Currently this is only the ESGF data archive:

.. image:: ../_images/tutorial/choose_source.png

Search Input Files
------------------

This is a search GUI to find appropriate files stored in ESGF data archive. 
By selecting a Search Categorie (blue buttons), you can choose the appropriate options (in orange). 

In this example select the following parameter: 

+----------------+------------+
| Categorie      | Option     |
+================+============+
| project        | CORDEX     |
+----------------+------------+
| domain         | WAS-44     | 
+----------------+------------+ 
| insitute       | MPI-CSC    |   
+----------------+------------+ 
| variable       |   tas      |   
+----------------+------------+
| time_frequency |   day      |
+----------------+------------+


Double selection (like two domains) can be realized with pressing *Ctrl* - tab. 

For the visualisation process it is necessary that the selected variable (``tas``) is the same as the
variable argument in the *Process Parameters*

And optionally you can set the time bounds:: 

    Start: 2005-01-01T12:00:00Z
    End:   2010-12-31T12:00:00Z 

The Selection should look similar to:

.. image:: ../_images/tutorial/esgf_search.png


Monitor running Job
-------------------

The job is now submitted and can be monitored in the *My Jobs* menue: 

.. image:: ../_images/tutorial/running_job.png

Now starts the current Job. The data will be downloaded. 
The data will be analyzed, due to the process. In this case, a field mean over the whole domain will be performed and an appropriate timeline drawn. 

When the job is finished, the status bar is tuning into green: 

.. image:: ../_images/statussucceeded.png

.. image:: ../_images/valuedownload.png

Click on the green *status succeeded* to get to the result of the submitted process.
In this case, it is an html Url. 
Opening it in a new browser tab gives the following result: 

.. image:: ../_images/tutorial/vis_plot.png








