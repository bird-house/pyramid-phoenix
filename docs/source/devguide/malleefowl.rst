.. _malleefowl:
Malleefowl WPS Processes
========================

Malleefowl is the server part of Birdhouse for WPS web processing
processes. Birdhouse uses PyWPS as the default web processing server
(There are alternatives like GeoServer, Cows, deegree, 52-North). The
Malleefowl component contains the currently available processes for
Birdhouse. Malleefowl has also some Python classes to simplify the
creation of new WPS processes and to define `source` and `worker`
processes which are used by the `Wizard` component in Phoenix. The
`Wizard` of Phoenix builds a workflow script with a `source` process
(retrievWing input files for `worker` processes) and a `worker` process
(processing one or more input files).

Important Note
--------------

The Malleefowl component has currently a *prototype*
status. Everything might change in the future.

Web Processing Services
-----------------------

I don't give an introdution to Web Processing Services here. *Please*
read the documentation of `PyWPS Tutorial`_, `OWSLib WPS`_ and `OGC WPS`_.

One remark. The WPS standard defines literal data types like int,
float, string, boolean, ... and a complex data type which we use for
file input and output. Read the docs for details :)

One more remark. WPS processes might be run synchronosly ore
asynchronosly. In Birdhouse we currently assume that all process are
async. This will change in the future.

Creating a WPS Process
======================

You can derive your WPS process directly from the PyWPS class
pywps.Process.WPSProcess. But it is recommended to use the adapted
Malleefowl class malleefowl.WPSProcess which simplifies the creation
of a new process.

Currently the Birdhouse components assumes that all process are run
asynchronus (read more about this in the WPS and PyWPS
documentation). The malleefowl WPSProcess class sets this by default.

To see an example of how to implement a WPS process check the already
available processes in the folder::

        $ cd $HOME/sandbox/src/Malleefowl/processes

To get startet see the process InOutProcess in testing.py which does
nothing special but defines all input and output types available in
PyWPS.


Creating a Source WPS Process
-----------------------------

The Wizard component of Phoenix (Birdhouse web-interface) generates a
workflow script with an Source process and an Worker process. The
Source process provides data files (for example netcdf files from
ESGF). The Worker process works on these data files (one or more) and
comes up with one or more result.

Source processes are derived form the Python class malleefowl.SourceProcess.

See the esgf source process as an example in `processes/esgf.py`.

Creating a Worker WPS Process
-----------------------------

These processes do the hard work on provided input data files. They
are used in the Wizard component of Phoenix for a chained workflow
process with a source and a worker process.

Worker processes are derived from the Python class malleefowl.WorkerProcess.

See the cdo process as an example of a worker process in `processes/cdo.py`.

.. _`OGC WPS`: http://www.opengeospatial.org/standards/wps
.. _`PyWPS`: http://pywps.wald.intevation.org/index.html
.. _`PyWPS Tutorial`: http://pywps.wald.intevation.org/documentation/course/process/index.html
.. _`OWSLib WPS`: http://geopython.github.io/OWSLib/#wps
