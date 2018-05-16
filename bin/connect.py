import sys
from collections import OrderedDict, Set
from typing import List
from pypika import Query, MSSQLQuery, PostgreSQLQuery, Table, Field
from pypyodbc import connect, Connection, DatabaseError
from collections import OrderedDict
from typing import List
from pypyodbc import connect, DatabaseError
from conf.db import DB_COLUMNS_TABLE, DB_COLUMN_COLUMN_NAME, DB_COLUMN_TABLE_NAME_FIELD
from convert import row_to_dict
from exceptions import UseOfAbstractForm


'''
------------------------------------------------------------------------------------------------------------------------
DataBase Object
------------------------------------------------------------------------------------------------------------------------
'''


class DataBase:
    """Holds the specifications for connecting to a database using the pypyodbc library and protocol"""
    def __init__(self, driver: str, server: str, port: str, db_name: str, user: str, pwd: str, trusted_source=False, verbose=False):
        self.driver = driver
        self.server = server
        self.port = port
        self.db_name = db_name
        self.user = user
        self.pwd = pwd
        self.trusted_source = trusted_source
        self.verbose = verbose
        self.db_columns_table = None
        self.db_column_column_name = None
        self.db_column_table_name_field = None

    def get_connection(self):
        """Returns a connection to the database referenced by this DataBase object."""
        if self.trusted_source:
            conn = self.get_connection_trusted_source()
        else:
            conn = self.get_connection_standard()
        return conn

    def get_connection_standard(self):
        """Makes a connection to the referenced database using standard authentication"""
        conn_string = "Driver={driver};Server={server};Port={port};Database={dbname};Uid={user};Pwd={pwd};"
        conn_string = conn_string.format(
            driver=self.driver, server=self.server, port=self.port, dbname=self.db_name, user=self.user, pwd=self.pwd)
        print('Connecting with the following specs:\n%s' % conn_string)
        return connect(conn_string)

    def get_connection_trusted_source(self):
        """Makes a connection to the referenced database using OS authentication"""
        conn_string = "Driver={driver};Server={server};Port={port};Database={dbname};Trusted_Connection=yes;"
        conn_string = conn_string.format(
            driver=self.driver, server=self.server, port=self.port, dbname=self.db_name)
        return connect(conn_string)

    def get_unique_elements(self, table: Table, field: Field):
        """Returns the unique values for a given field in a given table"""
        conn = self.get_connection()
        q = str(self.get_query_base()\
            .from_(table) \
            .select(field))
        results = conn.cursor().execute(q)
        return set([result[0] for result in results])

    def get_truncate_statement(self, table):
        """Truncate statements vary significantly between databases. This abstracts the specifications away"""
        raise UseOfAbstractForm('Attempted to generate truncate statement from abstract form of DataBase. Must use child instance.')

    def get_query_base(self):
        """Get the base QueryBuilder object for this type of database"""
        raise UseOfAbstractForm('Attempt to execute abstract form of DataBase object. Must use child object')

    # TODO: The constant values in this function (DB_COLUMNS_TABLE, DB_COLUMN_COLUMN_NAME, etc) should probably be made attributes of the DataBase object.
    def get_table_column_names(self, table: Table):
        conn = self.get_connection()
        q = str(self.get_query_base()\
            .from_(self.db_columns_table)\
            .select(self.db_column_column_name)\
            .where(self.db_column_table_name_field == table.table_name))
        return [result[0] for result in conn.cursor().execute(q)]

    def test_connection(self):
        """Try to connect to the database with the current connection specifications"""
        try:
            conn = self.get_connection()
            print('Successful connection.')
            conn.close()
        except DatabaseError as dbe:
            print('There is a problem with the connection:\n%s' % dbe.__str__())


class PostgreSQLDataBase(DataBase):
    def __init__(self, server, port, db_name, user, pwd, trusted_source=False, verbose=False):
        super().__init__('{PostgreSQL Unicode(x64)}', server, port, db_name, user, pwd, trusted_source, verbose)
        self.db_columns_table = Table('columns', schema='information_schema')
        self.db_column_column_name = Field('column_name')
        self.db_column_table_name_field = Field('table_name')

    def get_query_base(self):
        return PostgreSQLQuery

    def get_truncate_statement(self, table: Table):
        template = 'TRUNCATE '
        if table.schema is not None:
            table = table.schema + '.' + table.table_name
        else:
            table = table.table_name
        return template + table


class SQLServerDataBase(DataBase):
    def __init__(self, server, port, db_name, user, pwd, trusted_source=False, verbose=False):
        super().__init__('{SQL Server}', server, port, db_name, user, pwd, trusted_source, verbose)
        self.db_columns_table = Table('COLUMNS', schema='INFORMATION_SCHEMA')
        self.db_column_column_name = Field('COLUMN_NAME')
        self.db_column_table_name_field = Field('TABLE_NAME')

    def get_query_base(self):
        return MSSQLQuery

    def get_truncate_statement(self, table: Table):
        template = 'TRUNCATE '
        if table.schema is not None:
            table = table.schema + '.' + table.table_name
        else:
            table = table.table_name
        return template + table



"""
------------------------------------------------------------------------------------------------------------------------
TableVessel Object
------------------------------------------------------------------------------------------------------------------------
"""


class TableVessel:
    """Provides an interface to all values in a database table that correspond to a particular vessel."""
    def __init__(self, db: DataBase, table: Table, id_field: Field=None, id_value: int=None):
        self.id_field = id_field
        self.id_value = id_value
        self.table = table
        self.db = db

    # Fills the data package with the relevant data from the database
    def get_data(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        stmt = self.make_get_data_statement()
        print(stmt)
        cursor = cursor.execute(stmt)
        fields = self.db.get_table_column_names(self.table)
        for row in cursor:
            yield row_to_dict(fields, row)

    def write_data(self, data: List[OrderedDict]):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(self.make_write_data_statement(data))
        cursor.commit()
        conn.close()

    def truncate_table(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute((self.make_truncate_statement()))
        conn.close()

    def make_get_data_statement(self):
        return str(
            self.db.get_query_base()
            .from_(self.table).select('*')
            .where(self.id_field == self.id_value))


    def make_write_data_statement(self, data):
        fields = self.db.get_table_column_names(self.table)
        return str(
            self.db.get_query_base()
            .into(self.table)
            .columns(*fields)
            .insert(*[[row[field] for field in fields] for row in data]))

    def make_truncate_statement(self):
        template = 'TRUNCATE {schema}{table}'
        return template.format(schema=self.table.schema, table=self.table.table_name)
