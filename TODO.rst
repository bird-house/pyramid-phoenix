Todo list for Phoenix
=====================


Links
-----

* http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/quick_tutorial/index.html
* http://docs.pylonsproject.org/projects/deform/en/latest/index.html
* http://deformdemo.repoze.org/
* http://getbootstrap.com/2.3.2/index.html

Catalog Service
---------------

http://localhost:8082/csw?&service=CSW&version=2.0.2&request=GetRecords&typenames=csw:Record&elementsetname=full&resulttype=results&sortby=dc:title:D

Deployment
----------

* with docker and salt:

http://www.socallinuxexpo.org/scale12x/presentations/automated-deployment-django-docker-and-salt.html

Pyramid
-------

* use datetime json renderer:
http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/renderers.html#json-renderer
* use url dispatching for jobs, processes, outputs:
http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/quick_tutorial/routing.html
http://www.plope.com/weird_pyramid_urldispatch

* csw, wps and mongo not always avail when starting app. configure when accessed.
* email notification: pyramid-mailer, repoze.sendmail
* check *from pyramid.decorator import reify* for page_tile, breadcrumbs ... see kotti/views/utils.py

Wizard
--------

* https://github.com/repoze/repoze.workflow (see koti example)


Map
---

* setup wms caching, maybe just caching via nginx



Helsinki
--------

* DONE: enable openssl
https://wiki.apache.org/couchdb/Nginx_As_a_Reverse_Proxy
http://www.micahcarrick.com/using-ssl-behind-reverse-proxy-in-django.html
http://docs.gunicorn.org/en/latest/deploy.html
http://www.cyberciti.biz/faq/linux-unix-nginx-redirect-all-http-to-https/
http://ipython.org/ipython-doc/stable/notebook/public_server.html
http://nginx.org/en/docs/http/configuring_https_servers.html
http://www.cyberciti.biz/faq/linux-unix-nginx-redirect-all-http-to-https/
* DONE: by default install with unpriviledged user
* openid login box for dkrz etc
* DONE: configure esgf search node
* DONE: wizard: check if credential is valid
* DONE: check if token is valid
* DONE: upload files function in wps ui
http://docs.pylonsproject.org/projects/pyramid-deform/en/latest/
http://deform.readthedocs.org/en/latest/interfaces.html
* DONE: ipython notebook
* DONE: tutorial for phoenix
* DONE: using glob search for local files
* DONE: ipython examples for wps client (also chaining processes)
* DONE: configure admin users
* enable local admin user
* run test-suite in phoenix from ui
* DONE: esgf cache should stay longer (1 week?)

Bugs
----

* does not automatically add phoenix.socket in /var/run/phoenix (phoenix folder is missing)
Workaround: use /tmp/phoenix.socket
* owslib wps uses literaldata for inline complexdata ...
* DONE: upload complexdata in wizard was not enabled
* DONE: icons for settings
https://github.com/ipython/ipython/blob/master/docs/resources/ipynb_icon_64x64.png
* configure base wps in custom.cfg
* DONE: ipython proxy does not work with old nginx (ubuntu 12.04)
http://nginx.org/en/docs/http/websocket.html
http://stackoverflow.com/questions/22665809/how-to-configure-ipython-behind-nginx-in-a-subpath
https://chrislea.com/2013/02/23/proxying-websockets-with-nginx/
* wizard: get message "token updated successfully" also when update fails
* DONE: cdo sinfo etc: <Exception exceptionCode="MissingParameterValue" locator="file_identifier"/>
* DONE: no token when wps not avail at login: need update token button
* REJECTED: need index.html page on mouflon for redirect to port 80
* need to proxy ports for tomcat, wps, ...
* REJECTED: phoenix fails sometimes with: can't find command '../pyramid-phoenix/bin/phoenix.sh'
* wizard: cookie too long (need to use database)
* catalog: get_wps_with_auth fails
* DONE: get-wms files: use token (check map)


Common
------

* use mongodb from anaconda
* use seperate nginx config for proxy
* use supervisor to handle logging (via stdout?)
http://supervisord.org/configuration.html#programx-section
* enable bbox in ui
* backup mongodb
http://www.thegeekstuff.com/2013/09/mongodump-mongorestore/
* improve usage of install:prefix
* try linuxbrew
https://github.com/Homebrew/linuxbrew
https://github.com/mazzaroth/initpyr
* maybe run simple wf without restflow
* refactor phoenix.cfg
https://github.com/mazzaroth/initpyr
* configure browserid, openid:
  * http://www.rfk.id.au/blog/entry/painless-auth-pyramid-browserid/
  * http://quantumcore.org/docs/repoze.who.plugins.openid/
* DONE: show how long esgf certificate is valid
* run test-suite from ui (check common processes with nose)
* refactor wps schema, add token default value
* split phoenix logging for info, debug, ...
* using port 80 by default
* use common wpsmgr module: need common project for this
* maybe order processes by module name
* use comman methods for flashing messages
* check avail of wps in catalog
* testing with curl, http (script): see fossgis geo python
* configure buildout download
* DONE: configure caching for esg search
* integrate settings panel:
  http://www.ourtuts.com/34-outstanding-admin-panels-for-your-web-applications/
* see todopyramid as an example for table and json requests to wps without proxy
* fix nginx config for wps
* show wps service in result table
* DONE: allow login also when wps is not available
* check usage of thredds url in phoenix (incl. js) and malleefowl
* phoenix: thredds only avail as link in admin view 
* phoenix: get thredds url etc from malleefowl process
* phoenix: handle sessions
  http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html
* phoenix: make jobs repeateable 
* phoenix: show jobs input and ouput parameter
* DONE: configure admin users in custom.cfg
* phoenix: show currently logged in users
* DONE: refactorid admin/settings page (similar to macosx) 
* phoenix: update to latests pyramid
* DONE: rename phoenix to pyramid_phoenix
* SKIPPED: refresh button on job list
* wizard: add process name to notes
* opendap with date selection
* start/end selection for esgf files
* validate and visualize workflow before executing
* phoenix: integrate preview of results (using openlayers, pyngl, wms, ...)
* integrate phoenix logo
* dashboard with status and statistics
* show workflow results
* show wizard status
* need improved login panel with widgets
* use theme with larger font
  * http://getbootstrap.com/2.3.2/customize.html
* cancel and pause process
* maybe use metadata for gui: prio, group, restriction
* pywps/colander/form: allowedValues are interpreted with wrong type. "true" => True even though it
  should stay a string.

esg search widget
-----------------

* search with options for replica, versions, distrib
* use esg search querys with start/end time (use also bbox, height)
* show all possible values of a categorie with ctrl
* remove all tags
* remove all tags of a categorie (with delete)
* use paging for file list, tag box for selected files
* show time, bbox, variables, ... with file list

Low Priority
------------

* data selection favorites
* store favorite process input params
* store favorite esgf search selection

working on ui
-------------

* http://www.ourtuts.com/34-outstanding-admin-panels-for-your-web-applications/
* http://www.jquerysample.com/
* http://www.jqueryrain.com/example/bootstrap/

icon sets:

* http://www.famfamfam.com/lab/icons/silk/
* http://projects.opengeo.org/geosilk
* https://www.iconfinder.com/search/?q=iconset%3Afunction_icon_set
* http://p.yusukekamiyamane.com/


Research
--------

other web related frameworks:

* http://www.tornadoweb.org/en/stable/
* message queue - http://zeromq.org/
* message queue client - http://www.celeryproject.org/
* message queue - http://www.rabbitmq.com/tutorials/tutorial-one-python.html
* key value store - http://redis.io/
* smtp mail client - http://msmtp.sourceforge.net/


other web apps:

* http://ipython.org/notebook.html
* http://git-annex.branchable.com/assistant/
