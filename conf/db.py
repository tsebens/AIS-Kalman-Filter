from pypika import Table, Field

from connect import SQLServerDataBase, PostgreSQLDataBase

"""
----------------------------------------------------------------
DATABASE CONFIGURATION
----------------------------------------------------------------
"""
server = r'localhost'
port = '5432'
dbname = 'kalman'
user = 'tristan.sebens'
pwd = ''
trusted = False # Tells the connection to use OS authentication or not

"""
----------------------------------------------------------------
DATABASE CONNECTION
----------------------------------------------------------------
The database connection produced by the specifications contained in this file
"""
db = PostgreSQLDataBase(server, port, dbname, user, pwd, trusted_source=trusted)

"""
----------------------------------------------------------------
INPUT
----------------------------------------------------------------
"""
INPUT_TABLE = Table("VMS_TEST_VOYAGE", schema='public')
# The field the filter will use to distinguish individual vessels
ID_FIELD_NAME = "VESSEL_ID"
ID_FIELD = Field(ID_FIELD_NAME, table=INPUT_TABLE)
# Fieldname for the longitude values
LON_FIELD_NAME = "LONGITUDE"
LON_FIELD = Field(LON_FIELD_NAME, table=INPUT_TABLE)
# Fieldname for the latitude values
LAT_FIELD_NAME = "LATITUDE"
LAT_FIELD = Field(LAT_FIELD_NAME, table=INPUT_TABLE)
# Fieldname for the timestamp values
TIMESTAMP_FIELD_NAME = "POSITION_DATETIME"
TIMESTAMP_FIELD = Field(TIMESTAMP_FIELD_NAME, table=INPUT_TABLE)


"""
----------------------------------------------------------------
OUTPUT
----------------------------------------------------------------
"""
OUTPUT_TABLE = Table("VMS_TEST_VOYAGE_FILTERED", schema='public')
# Fieldname for the output longitude values
OUTPUT_LON_FIELD_NAME = "FILT_LON"
OUTPUT_LON_FIELD = Field(OUTPUT_LON_FIELD_NAME, table=OUTPUT_TABLE)
# Fieldname for the output latitude values
OUTPUT_LAT_FIELD_NAME = "FILT_LAT"
OUTPUT_LAT_FIELD = Field(OUTPUT_LAT_FIELD_NAME, table=OUTPUT_TABLE)
# Fieldname for the output deviance values
OUTPUT_DEV_FIELD_NAME = "DEVIANCE"
OUTPUT_DEV_FIELD = Field(OUTPUT_DEV_FIELD_NAME, table=OUTPUT_TABLE)

"""
----------------------------------------------------------------
STATIC DATABASE FIELDS
----------------------------------------------------------------
"""
# The DB table where column names are stored.
DB_COLUMNS_TABLE = Table('columns', schema='information_schema') # Configured for PostgreSQL DB
# The field in the column name table that stores the column names
DB_COLUMN_COLUMN_NAME = Field('column_name')
# The field in the column name table that stores the table names
DB_COLUMN_TABLE_NAME_FIELD = Field('table_name')
