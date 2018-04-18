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

# The DB table where column names are stored.
DB_COLUMNS_TABLE = Table('columns', schema='information_schema') # Configured for PostgreSQL DB
# The field in the column name table that stores the column names
DB_COLUMN_COLUMN_NAME = Field('column_name')
# The field in the column name table that stores the table names
DB_COLUMN_TABLE_NAME_FIELD = Field('table_name')