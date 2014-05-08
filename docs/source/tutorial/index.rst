.. _tutorial:

********
Tutorial
********

Phoenix is a Web Processing Service (WPS) for the earth systhem modelling community. The service offers an easy to use graphical user interface as a valuable practical tool to process and analyze big data. WPS represents an interface to perform processes over the HTTP network protocol, enabling users to trigger processes over a website. 

In the following tutorial will guide you though the first stepps to get familliar with Phoenix. 

-----------------------------
**Login and Accout settings**
-----------------------------

The login is realized with your personal openID of ESGF. Make sure, that you have a valid openID of one of the ESGF datanodes (http://esgf-data.dkrz.de/esgf-web-fe/) and that you at least once were able to download a datafile. 

You will find the login in the upper right corner: 

.. image:: signin.png

Enter your personal openID. Please use the full path:

.. image:: openid.png

And enter you appropriate password. 
In the current state of Phoenix (May 2014) you have to be personally activated in the Phoenix-WPS. 
If you are not activated please contact Nils Hempelmann (nils.hempelmann@hzg.de) with an sort description of your motivation to use Phoenix.

With a sucessful login your token is updated and valid as well:

.. image:: access_status_sucess.png

The token as well as your security cetificate (necessary to access the ESGF data archive ) can be seen and updated under *My Account*: 

.. image:: accout_settings.png

For security reasons the certificate and the token is time limited valid. But don't worry; Phoenix will remind you to update if necessary:

.. image:: expire.png


--------------------------------
**Creating some overview plots**
--------------------------------

Once the login procedure is done, processes are operable and data search and download within the ESGF data archive is possible. 
There are two ways to submit a process: 

- Processes
or 

- Wizard

While with *Processes* you can select single operational processes the *Wizard* is guiding you through the necessary stepps to submit a job. For getting an idea of the operation procedure choose the *Wizard* menue and select **simple**: 

.. image:: wizard.png

And check the listed *PyWPS Server on mouflon.dkrz.de (mouflon)* . 
With clicking on *Next* you'll find the list of available processes. 
Check the **Visualisation of data** and klick on *Next* which guides you to the process parameter: 

.. image:: processparameter.png










Calculation of summer days per year 


Future
------

This will all change in future ...