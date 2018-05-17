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
 - __init___.py
 - func.py
 - db.py
 - filter.py
 - static.py

Ignore the first two.

db.py is used to set configuration values relevant to the database the filter will be interfacing with.
These are the important values:
 - INPUT_TABLE  - This is the table that the filter is going to read in it's values from.
 - OUTPUT_TABLE - Where the filter is going to write it's output
 - ID_FIELD     - The field the filter will use to identify individual vessels from within the table
 - LAT_FIELD    - The field name of the column containing the table's latitude values
 - LON_FIELD    - The field name of the column containing the table's longitude values