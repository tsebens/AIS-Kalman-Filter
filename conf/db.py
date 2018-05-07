from pypika import Table, Field
"""
--------------------------------------------------------------------------------------------
Database connection configuration
--------------------------------------------------------------------------------------------
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
# The field the filter will use to distinguish individual vessels
ID_FIELD = Field("VESSEL_ID")


# The DB table where column names are stored.
DB_COLUMNS_TABLE = Table('COLUMNS', schema='INFORMATION_SCHEMA') # Configured for PostgreSQL DB
# The field in the column name table that stores the column names
DB_COLUMN_COLUMN_NAME = Field('COLUMN_NAME')
# The field in the column name table that stores the table names
DB_COLUMN_TABLE_NAME_FIELD = Field('TABLE_NAME')
