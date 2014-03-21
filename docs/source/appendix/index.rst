.. _appendix:

********
Appendix
********

============
WPS Software
============

WPS Server Software:

* PyWPS - https://github.com/geopython/PyWPS
* GeoServer - http://docs.geoserver.org/stable/en/user/extensions/wps/processes.html
* Zoo - http://www.zoo-project.org
* COWS - http://ceda-wps2.badc.rl.ac.uk/docs/cows_wps/intro.html
* Deegree - http://www.deegree.org/
* 52 North - http://52north.org/communities/geoprocessing/wps/

WPS Client Software:

* OWSLib - http://geopython.github.io/OWSLib/
* OpenLayers WPS Plugin - http://dev.openlayers.org/docs/files/OpenLayers/WPSClient-js.html
* GeoTools WPS Module - http://docs.geotools.org/latest/userguide/unsupported/wps.html

=========================
Scientific Workflow Tools
=========================
    
Workflow Engines:

* RestFlow - https://github.com/restflow-org/restflow/wiki
* Taverna - http://www.taverna.org.uk/
* VisTrails - http://www.vistrails.org/index.php/Main_Page
* Kepler - https://kepler-project.org/

Taverna with WPS:

* http://rsg.pml.ac.uk/wps/generic.cgi?request=GetCapabilities&service=WPS
* http://www.youtube.com/watch?v=JNAtoOejVIo
* http://www.taverna.org.uk/introduction/services-in-taverna/  
* https://github.com/myGrid/small-area-estimator
* http://comments.gmane.org/gmane.science.biology.informatics.taverna.user/1415
* http://dev.mygrid.org.uk/wiki/display/developer/SCUFL2

VisTrails with WPS:

* http://code.google.com/p/eo4vistrails/
* http://proj.badc.rl.ac.uk/cows/wiki/CowsWps/CDOWPSWorkingGroup/WPSAndWorkflows  
* http://www.kitware.com/source/home/post/105

Kepler with WPS:

* https://kepler-project.org/users/sample-workflows

Other Workflow Engines:

* http://www.yawlfoundation.org/
* http://en.wikipedia.org/wiki/Scientific_workflow_system
* http://airavata.apache.org/
* http://search.cpan.org/~nuffin/Class-Workflow-0.11/

Related Projects:

* http://climate4impact.eu/impactportal/general/index.jsp
* http://adaguc.knmi.nl/
* http://evolvingweb.github.io/ajax-solr/examples/reuters/index.html
* http://ceda-wps2.badc.rl.ac.uk/ui/home


=================
Scientific Python
=================

* Anaconda - https://store.continuum.io/cshop/anaconda/

Completely free enterprise-ready Python distribution for large-scale
data processing, predictive analytics, and scientific computing

* pandas - http://pandas.pydata.org/

Python Data Analysis Library

=========================
Python in Climate Science
========================= 

* OpenClimateGIS - https://earthsystemcog.org/projects/openclimategis/

OpenClimateGIS is a Python package designed for geospatial
manipulation, subsetting, computation, and translation of climate
datasets stored in local NetCDF files or files served through THREDDS
data servers. [..]

* ICCLIM (i see clim ...) - https://github.com/tatarinova/icclim

Python library for climate indices calculation. 
Documentation at http://icclim.readthedocs.org/

===============================
Python Web Frameworks and Utils
===============================

* Authomatic - http://peterhudec.github.io/authomatic/

====================
Example WPS Requests
====================

WPS Documentation with examples: 

http://geoprocessing.info/wpsdoc/1x0GetCapabilities

Get WPS Capabilities:

http://mouflon.dkrz.de:8090/wps?Request=GetCapabilities&Service=WPS

Describe Process:

http://mouflon.dkrz.de:8090/wps?service=WPS&request=DescribeProcess&version=1.0.0&identifier=org.malleefowl.test.add

Execute Process:

http://mouflon.dkrz.de:8090/wps?service=WPS&request=Execute&version=1.0.0&identifier=org.malleefowl.test.add&DataInputs=num_a=1.0;num_b=2.0

Execute Process, Result XML containing output (asReference=false):

http://mouflon.dkrz.de:8090/wps?service=WPS&request=Execute&version=1.0.0&identifier=org.malleefowl.test.add&DataInputs=num_a=1.0;num_b=2.0&responsedocument=output=@asreference=false 

Execute Process Async:

http://mouflon.dkrz.de:8090/wps?service=WPS&request=Execute&version=1.0.0&identifier=org.malleefowl.test.add&DataInputs=num_a=1.0;num_b=2.0&storeExecuteResponse=true&status=true

Execute Process, Raw output:

http://mouflon.dkrz.de:8090/wps?service=WPS&request=Execute&version=1.0.0&identifier=org.malleefowl.test.add&DataInputs=num_a=1.0;num_b=2.0&rawdataoutput=output

====================
Example WPS Services
====================

List of available Web Processing Services:

* GeoServer Demo WPS - http://demo.opengeo.org/geoserver/wps?request=GetCapabilities&service=WPS
* Plymoth Marine Laboratory - http://rsg.pml.ac.uk/wps/generic.cgi?request=GetCapabilities&service=WPS
* Plymoth Marine Laboratory - http://rsg.pml.ac.uk/wps/vector.cgi?request=GetCapabilities&service=WPS
* USGS Geo Data Portal- http://cida.usgs.gov/climate/gdp/process/WebProcessingService
* KNMI climate4impact Portal - http://climate4impact.eu//impactportal/WPS?request=GetCapabilities&service=WPS
* BADC CEDA - http://ceda-wps2.badc.rl.ac.uk/wps?request=GetCapabilities&service=WPS 



