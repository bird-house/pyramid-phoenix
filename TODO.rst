Todo list for Phoenix
=====================

Common
------

* configure defaults for custom.cfg
* use https:
  http://nginx.org/en/docs/http/configuring_https_servers.html
* fix nginx config for wps
* show wps service in result table
* allow login also when wps is not available
* check usage of thredds url in phoenix (incl. js) and malleefowl
* phoenix: thredds only avail as link in admin view 
* phoenix: get thredds url etc from malleefowl process
* phoenix: handle sessions
  http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/sessions.html
* phoenix: make jobs repeateable 
* phoenix: show jobs input and ouput parameter
* phoenix: configure admin users in custom.cfg
* phoenix: show currently logged in users
* phoenix: caching esgf search does not work
* phoenix, malleefowl: simplify access params to esgf and publish
* phoenix: refactorid admin/settings page (similar to macosx) 
* phoenix: use stored openid as default value in wizard and process
* phoenix: update to latests pyramid
* rename phoenix to pyramid_phoenix
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
* rework output param form
* need improved login panel with widgets
* use theme with larger font
  * http://getbootstrap.com/2.3.2/customize.html
* cancel and pause process
* use flash: self.request.session.flash(u"Your changes have been saved.")
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
