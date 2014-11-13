Todo list
*********

Bugs
====

* conda wget build works only either for centos or debian
* debian wget does not work for esgf downloads
* phoenix: enter "!" in text field breaks wps execution
  seams to be an owslib wps bug, need test case
* IE (at least some versions) do not work with Phoenix (pyramid framework)
* pywps/colander/form: allowedValues are interpreted with wrong type. "true" => True even though it
  should stay a string.
* with gunicorn=19 no error messsages written to supervisor in case of error


Common
======

* upgrade to buildout 2
* add link to fatcow icons
http://www.fatcow.com/free-icons
* install malleefowl with phoenix
* configure wpscache urls ...
* set anaconda_home in user env
* clean up view templates
* download process (wget script generator)
* loop workflow
* store timestamps in UTC. Handle user timezone.
* csw, wps and mongo not always avail when starting app. configure when accessed.
* check *from pyramid.decorator import reify* for page_tile, breadcrumbs ... see kotti/views/utils.py
* enable bbox in ui
* testing with curl, http (script): see fossgis geo python

Login
=====

* add more esgf providers to esgf login
* trust by default esgf openids
* improve local login
* configure admin (roles) with mongodb

Views
=====

* ...

Settings
========

* show jobs by user
* refactor users settings view (use title renderer)

Outputs
=======

* run same job again

Wizard
======

* maybe skip egsf file selection. do it in background (just get time-range and variable).
* refactor appstruct handling ...
* dont use default form buttons
* replace esgf file widget
* if update creds fails dont go to next step
* start restflow as service
* add search facets to job keywords
* show only processes with complex parameters
* use mimetype as filter in search
* use workflow module:
https://github.com/repoze/repoze.workflow (see koti example)
* esgf file list does not restore state
* refactor state storage 


Map
===

* add layers from catalog ... see catalog viewer
* setup wms caching, maybe just caching via nginx

ESGF Search
===========

* use paging for file list, tag box for selected files
* show time, bbox, variables, ... with file list












