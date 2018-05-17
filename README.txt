AIS Kalman filter

Developed for NMFS by Tristan Sebens
tristan.ng.sebens@gmail.com
907-500-5430

This intent of this application is to process marine gps sensor data which is assumed to be relatively noisy and
inaccurate, and to estimate the likely path of the vessel based on both the incoming data and a set of defined
rules which are intended to model the manner in which a vessel typically behaves.

CONFIGURATION OPTIONS:
This script is written to be (relatively) easily configurable by the end user. In particular, you can point the script
at any table, and you can set global variable which are used by the filter to evaluate the behavior of the vessels.

The configuration of the filter is controlled by the files in the 'conf' directory. Inside of this directory there should
be 5 files:
 - db.py
 - filter.py
 - static.py
 - __init___.py
 - func.py

__init__.py and func.py are system files. Ignore them.


--------------------
db.py
--------------------
db.py is used to set configuration values relevant to the database the filter will be interfacing with. You can specify
all of the connection parameters here (server, port, db name, user, pwd). This is also where you will configure which
parts of the database the filter will interact with:

INPUT VALUES:
 - INPUT_TABLE          - This is the table that the filter is going to read in it's values from.
 - OUTPUT_TABLE         - Where the filter is going to write it's output
 - ID_FIELD_NAME        - The field the filter will use to identify individual vessels from within the table
 - LAT_FIELD_NAME       - The field name of the column containing the table's latitude values
 - LON_FIELD_NAME       - The field name of the column containing the table's longitude values
 - TIMESTAMP_FIELD_NAME - The field name of the column containing the table's timestamps
OUTPUT VALUES
 - OUTPUT_LAT_FIELD_NAME - The field name of the column where the filter will write it's filtered latitude
 - OUTPUT_LON_FIELD_NAME - The field name of the column where the filter will write it's filtered latitude
 - OUTPUT_DEV_FIELD_NAME - The field name of the column where the filter will write the deviance value


--------------------
filter.py
--------------------
This is where you can select the methods that the filter will use to perform it's prediction and estimation steps for each
variable in the agent state. Right now there are no methods implemented other than the ones that are in use, so for now
there's nothing to do here.



--------------------
static.py
--------------------
This is where you can set global constants that will adjust and limit the calculations made by the filter. Currently, only
one of the values in this file is used:

MAX_ALLOWABLE_VESSEL_SPEED

This sets the maximum speed a theoretical vessel is capable of achieving. It is measured in meters/second, so if you want
to set the value in knts, you will need to use the conversion function knts_to_mps(knts) to convert the value.