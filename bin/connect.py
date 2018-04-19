from collections import OrderedDict, Set
from typing import List
from pypika import Query, MSSQLQuery, PostgreSQLQuery, Table, Field

from pypyodbc import connect, Connection, DatabaseError

from conf.db import DB_COLUMNS_TABLE, DB_COLUMN_COLUMN_NAME, DB_COLUMN_TABLE_NAME_FIELD
from exceptions import UseOfAbstractForm

'''
------------------------------------------------------------------------------------------------------------------------
DataBase Object
------------------------------------------------------------------------------------------------------------------------
'''
class DataBase:
    """Holds the specifications for connecting to a database using the pypyodbc library and protocol"""
    def __init__(self, driver: str, server: str, port: str, db_name: str, user: str, pwd: str, trusted_source=False):
        self.driver = driver
        self.server = server
        self.port = port
        self.db_name = db_name
        self.user = user
        self.pwd = pwd
        self.trusted_source = trusted_source

    def get_connection(self):
        """Returns a connection to the database referenced by this DataBase object."""
        if self.trusted_source:
            return self.get_connection_trusted_source()
        else:
            return self.get_connection_standard()

    def get_connection_standard(self):
        """Makes a connection to the referenced database using standard authentication"""
        conn_string = "Driver={driver};Server={server};Port={port};Database={dbname};Uid={user};Pwd={pwd};"
        conn_string = conn_string.format(
            driver=self.driver, server=self.server, port=self.port, dbname=self.db_name, user=self.user, pwd=self.pwd)
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
        q = self.get_query_base()\
            .from_(table) \
            .select(field)
        results = conn.cursor().execute(q)
        return Set(results)

    def get_truncate_statement(self, table):
        """Truncate statements vary significantly between databases. This abstracts the specifications away"""
        raise UseOfAbstractForm('Attempted to generate truncate statement from abstract form of DataBase. Must use child instance.')

    def get_query_base(self):
        """Get the base QueryBuilder object for this type of database"""
        raise UseOfAbstractForm('Attempt to execute abstract form of DataBase object. Must use child object')

    def test_connection(self):
        """Try to connect to the database with the current connection specifications"""
        try:
            self.get_connection()
        except DatabaseError as dbe:
            print('There is a problem with the connection:\n%s' % dbe.__str__())


class PostgreSQLDataBase(DataBase):
    def __init__(self, server, port, db_name, user, pwd):
        self.driver = '{PostgreSQL Unicode(x64)}'
        self.server = server
        self.port = port
        self.db_name = db_name
        self.user = user
        self.pwd = pwd

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
    def __init__(self, server, port, db_name, user, pwd):
        self.driver = '{SQL Server}'
        self.server = server
        self.port = port
        self.db_name = db_name
        self.user = user
        self.pwd = pwd

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
        self.conn = db.get_connection()

    # Fills the data package with the relevant data from the database
    def get_data(self):
        cur = self.conn.cursor()
        return [make_row_dict(self.get_table_column_names(self.table), row) for row in cur.execute(self.make_get_data_statement())]

    def write_data(self, data: List[OrderedDict]):
        cursor = self.conn.cursor()
        cursor.execute(self.make_write_data_statement(data))
        cursor.commit()

    def truncate_table(self):
        cursor = self.conn.cursor()
        cursor.execute((self.make_truncate_statement()))

    def make_get_data_statement(self):
        return str(
            self.db.get_query_base()
            .from_(self.table).select('*')
            .where(self.id_field == self.id_value))

    def make_write_data_statement(self, data):
        return str(
            self.db.get_query_base()
            .into(self.table)
            .columns(*self.get_table_column_names(self.table))
            .insert(*[[row[field] for field in row.keys()] for row in data]))

    def make_truncate_statement(self):
        template = 'TRUNCATE {schema}{table}'
        return template.format(schema=self.table.schema, table=self. table.table_name)

    # TODO: The constant values in this function (DB_COLUMNS_TABLE, DB_COLUMN_COLUMN_NAME, etc) should probably be made attributes of the DataBase object.
    def get_table_column_names(self, table: Table):
        q = self.get_query_base()\
            .from_(DB_COLUMNS_TABLE)\
            .select(DB_COLUMN_COLUMN_NAME)\
            .where(DB_COLUMN_TABLE_NAME_FIELD == table.table_name)
        return [result[0] for result in self.conn.cursor().execute(str(q))]


def connect_to_db(driver, server, port, dbname, user, pwd):
    conn_string = "Driver={driver};Server={server};Port={port};Database={dbname};Uid={user};Pwd={pwd};"
    conn_string = conn_string.format(driver=driver, port=port, server=server, dbname=dbname, user=user, pwd=pwd)
    print('Connecting with this connection string:\n%s' % conn_string)
    return connect(conn_string)


# Creates an ordered dict object from a list of fields and a list of values.
def make_row_dict(fields, row):
    row_dict = {}
    for i in range(len(fields)):
        row_dict[fields[i]] = row[i]
    return row_dict