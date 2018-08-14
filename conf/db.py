from pypika import Table, Field

"""
----------------------------------------------------------------
DATABASE CONFIGURATION
----------------------------------------------------------------
"""
server = r'akr-j53\PROD'
port = '1433'
dbname = 'CATCH_IN_AREAS'
user = ''
pwd = ''

"""
----------------------------------------------------------------
INPUT
----------------------------------------------------------------
"""
INPUT_TABLE = Table("STG_VMS", schema='dbo')
# The field the filter will use to distinguish individual vessels
ID_FIELD_NAME = "VESSEL_ID"
ID_FIELD = Field(ID_FIELD_NAME)
# Fieldname for the longitude values
LON_FIELD_NAME = "LONGITUDE"
LON_FIELD = Field(LON_FIELD_NAME)
# Fieldname for the latitude values
LAT_FIELD_NAME = "LATITUDE"
LAT_FIELD = Field(LAT_FIELD_NAME)
# Fieldname for the timestamp values
TIMESTAMP_FIELD_NAME = "POSITION_DATETIME"
TIMESTAMP_FIELD = Field(TIMESTAMP_FIELD_NAME)


"""
----------------------------------------------------------------
OUTPUT
----------------------------------------------------------------
"""
OUTPUT_TABLE = Table("stg_vms_test", schema='dbo')
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
DB_COLUMNS_TABLE = Table('columns', schema='information_schema') # Configured for PostgreSQL DB
# The field in the column name table that stores the column names
DB_COLUMN_COLUMN_NAME = Field('column_name')
# The field in the column name table that stores the table names
DB_COLUMN_TABLE_NAME_FIELD = Field('table_name')
