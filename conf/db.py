from pypika import Table, Field
"""
----------------------------------------------------------------
DATABASE CONFIGURATION
----------------------------------------------------------------
"""

server = 'localhost'
port = '6000'
dbname = 'kalman'
user = 'tristan.sebens'
pwd = ''

# The table where the filter will write it's outputs
INPUT_TABLE = Table('PROBLEM_VMS_DATASET', schema='public')
# The table where the filter will look for inputs
OUTPUT_TABLE = Table('stg_vms_test', schema='public')

"""
----------------------------------------------------------------
INPUT FIELDS
----------------------------------------------------------------
"""
# The field the filter will use to distinguish individual vessels
ID_FIELD_NAME = "VESSEL_ID"
# Fieldname for the longitude values
LON_FIELD_NAME = "LONGITUDE"
# Fieldname for the latitude values
LAT_FIELD_NAME = "LATITUDE"
# Fieldname for the timestamp values
TIMESTAMP_FIELD_NAME = "POSITION_DATETIME"

"""
----------------------------------------------------------------
OUTPUT FIELDS
----------------------------------------------------------------
"""
# Fieldname for the output longitude values
OUTPUT_LON_FIELD_NAME = "filt_lon"
# Fieldname for the output latitude values
OUTPUT_LAT_FIELD_NAME = "filt_lat"
# Fieldname for the output deviance values
OUTPUT_DEV_FIELD_NAME = "deviance"

"""
----------------------------------------------------------------
STATIC DATABASE FIELDS
----------------------------------------------------------------
"""
# The DB table where column names are stored.
DB_COLUMNS_TABLE = Table('COLUMNS', schema='INFORMATION_SCHEMA') # Configured for PostgreSQL DB
# The field in the column name table that stores the column names
DB_COLUMN_COLUMN_NAME = Field('COLUMN_NAME')
# The field in the column name table that stores the table names
DB_COLUMN_TABLE_NAME_FIELD = Field('TABLE_NAME')
