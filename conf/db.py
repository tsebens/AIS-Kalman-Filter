from pypika import Table, Field

"""
--------------------------------------------------------------------------------------------
Database connection configuration
--------------------------------------------------------------------------------------------
"""
server = r'akr-j98\PROD'
port = '1433'
dbname = 'CATCH_IN_AREAS'
user = ''
pwd = ''

# The table where the filter will look for inputs
INPUT_TABLE = Table('VMS', schema='dbo')
# The table where the filter will write it's outputs
OUTPUT_TABLE = Table('VMS_Filter', schema='dbo')
# The field the filter will use to distinguish individual vessels
ID_FIELD = Field("VESSEL_ID")




# The DB table where column names are stored.
DB_COLUMNS_TABLE = Table('columns', schema='information_schema') # Configured for PostgreSQL DB
# The field in the column name table that stores the column names
DB_COLUMN_COLUMN_NAME = Field('column_name')
# The field in the column name table that stores the table names
DB_COLUMN_TABLE_NAME_FIELD = Field('table_name')
