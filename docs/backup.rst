mongodb
*******

dump mondodb::
   
   $ mongodump

export users collection::

   $ mongoexport -db phoenix_db -collection users -out users.json

import users in mongodb::

   $ mongoimport --db phoenix_db --collection users --file users.json
