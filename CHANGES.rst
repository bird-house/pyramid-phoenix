Changes
*******

0.2.2 (current)
==================

* sends email to admin users on user login failure.
* uses user name from openid parameters.
* pcmdi and smhi added to esgf login page.
* shows last login in users settings.
* shows unregistered users in dashboard.

0.2.1 (2014-11-11)
==================

* Using Makefile from birdhousebuilder.bootstrap to install and start application.
* Fixed signin urls on register page.


0.2.0 (2014-09-04)
==================

Paris Release


* moved code to github
* choose licence: apache license version 2.0
  http://www.apache.org/licenses/
* setup proxy for openlayers and js to access thredds, esgf-search ...
  https://github.com/gwaldron/godzi-webgl/blob/master/tests/proxy.php
  http://trac.osgeo.org/openlayers/wiki/FrequentlyAskedQuestions#ProxyHost
  http://wiki.nginx.org/HttpFastcgiModule
* configure base malleefowl wps + additional wps from catalog service
* use simple wps calls in wizard for listings etc ...
* use wps chain for restflow process
* reduce number of wps initialisations in wizard
* uses datetime json renderer:
http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/renderers.html#json-renderer
* dashboard added
* refactored wizard

Bugs

* time selection does not filter mon cordex files in esg file search
* init of wps fails (e.a when wps is registered but not avail)
* fix port 80 config (browserid ...)
* notes and tags missing in job list

0.1.1 (2014-05-20)
==================

Helsinki Release

* added ipython notebook tutorials

0.1.0 (2013-12-10)
==================

Hamburg Release

