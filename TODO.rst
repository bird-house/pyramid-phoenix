Todo list
*********

Bugs
====

* phoenix: enter "!" in text field breaks wps execution
  seams to be an owslib wps bug, need test case
* IE (at least some versions) do not work with Phoenix (pyramid framework)
* pywps/colander/form: allowedValues are interpreted with wrong type. "true" => True even though it
  should stay a string.


Common
======

* store timestamps in UTC. Handle user timezone.
* use datetime json renderer:
http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/renderers.html#json-renderer
* csw, wps and mongo not always avail when starting app. configure when accessed.
* email notification: pyramid-mailer, repoze.sendmail
* check *from pyramid.decorator import reify* for page_tile, breadcrumbs ... see kotti/views/utils.py
* enable bbox in ui
* testing with curl, http (script): see fossgis geo python
* make jobs repeateable 

Outputs
=======

* update message text with js does not work
* show wps error messages in output list
* run same job again

Wizard
======

* https://github.com/repoze/repoze.workflow (see koti example)
* esgf file list does not restore state
* csw search does not restore state

Map
===

* setup wms caching, maybe just caching via nginx

ESGF Search
===========

* use paging for file list, tag box for selected files
* show time, bbox, variables, ... with file list












