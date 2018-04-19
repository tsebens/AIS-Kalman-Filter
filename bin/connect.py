from collections import OrderedDict, Set
from typing import List
from pypika import Query, Table, Field
from pypyodbc import connect, Connection, DatabaseError
from conf.db import DB_COLUMNS_TABLE, DB_COLUMN_COLUMN_NAME, DB_COLUMN_TABLE_NAME_FIELD


class DataBase:
    """Holds the specifications for connecting to a database using the pypyodbc library and protocol"""
    def __init__(self, driver, server, port, db_name, user, pwd):
        self.driver = driver
        self.server = server
        self.port = port
        self.db_name = db_name
        self.user = user
        self.pwd = pwd

    def get_connection(self):
        conn_string = "Driver={driver};Server={server};Port={port};Database={dbname};Uid={user};Pwd={pwd};"
        print('Connecting with the following specs:\n%s' % conn_string)
        conn_string = conn_string.format(
            driver=self.driver, server=self.server, port=self.port, dbname=self.db_name, user=self.user, pwd=self.pwd)
        return connect(conn_string)

    def get_ids(self, table: Table, id_field: Field):
        conn = self.get_connection()
        q = Query\
            .from_(table)\
            .select(id_field)
        q = str(q).replace('\"', '')
        results = conn.cursor().execute(q)
        ret = set([str(result[0]) for result in results])
        conn.close()
        return ret

    def test_connection(self):
        try:
            conn = self.get_connection()
        except DatabaseError as dbe:
            print('Connection not working.')
            return
        print('Connection healthy.')


class PostgreSQLDataBase(DataBase):
    def __init__(self, server, port, db_name, user, pwd):
        self.driver = '{PostgreSQL Unicode(x64)}'
        self.server = server
        self.port = port
        self.db_name = db_name
        self.user = user
        self.pwd = pwd


class SQLServerDataBase(DataBase):
    def __init__(self, server, port, db_name, user, pwd):
        self.driver = '{SQL Server}'
        self.server = server
        self.port = port
        self.db_name = db_name
        self.user = user
        self.pwd = pwd

    def get_connection(self):
        conn_string = "Driver={driver};Server={server};Port={port};Database={dbname};Trusted_Connection=yes;"
        conn_string = conn_string.format(driver=self.driver, port=self.port, server=self.server, dbname=self.db_name)
        print('Connecting with the following specs:\n%s' % conn_string)
        return connect(conn_string)


class TableVessel:
    """Provides an interface to all values in a database table that correspond to a particular vessel. Those values will be identified by the id field and the id value"""
    def __init__(self, conn: Connection, table: Table, id_field: Field=None, id_value: int=None):
        self.id_field = id_field
        self.id_value = id_value
        self.table = table
        self.conn = conn
        # self.init_connection() # TODO: Decide whether or not to keep this

    def init_connection(self):
        self.conn.connect()

    # Fills the data package with the relevant data from the database
    def get_data(self):
        q = Query\
            .from_(self.table).select('*')\
            .where(self.id_field == self.id_value)
        q = str(q).replace('\"', '')
        cur = self.conn.cursor()
        return [make_row_dict(column_names(cur), row) for row in cur.execute(str(q))]

    def write_data(self, data: List[OrderedDict], fields, truncate=False):
        cursor = self.conn.cursor()
        if truncate:
            q = self.make_truncate_statement()
            cursor.execute(str(q))
        q = self.make_write_statement(data, fields)
        q = str(q).replace('\"', '')
        print(q)
        cursor.execute(q)
        cursor.commit()

    def make_write_statement(self, data, fields):
        #[[row[field] for field in fields] for row in data]
        q = Query\
            .into(self.table)\
            .columns(fields)
        for row in data:
            q.insert([row[field] for field in fields])
        return str(q) + ';'

    def make_truncate_statement(self):
        template = 'TRUNCATE {schema}{table}'
        return template.format(schema=self.table.schema, table=self.table.table_name)

    def get_column_names(self):
        return get_table_column_names(self.conn, self.table)


# TODO: The constant values in this function (DB_COLUMNS_TABLE, DB_COLUMN_COLUMN_NAME, etc) should probably be made attributes of the DataBase object.
def get_table_column_names(conn: Connection, table: Table):
    q = Query\
        .from_(DB_COLUMNS_TABLE)\
        .select(DB_COLUMN_COLUMN_NAME)\
        .where(DB_COLUMN_TABLE_NAME_FIELD == table.table_name)
    q = str(q).replace('\".\"', '.')
    q = 'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME=\'dbo.stg_vms_test\''
    print(q)
    return [result[0] for result in conn.cursor().execute(str(q))]


def connect_to_db(driver, server, port, dbname, user, pwd):
    conn_string = "Driver={driver};Server={server};Port={port};Database={dbname};Uid={user};Pwd={pwd};"
    conn_string = conn_string.format(driver=driver, port=port, server=server, dbname=dbname, user=user, pwd=pwd)
    print('Connecting with this connection string:\n%s' % conn_string)
    return connect(conn_string)


def enclose_values_in_parentheses(iter, enclose=''):
    template = "("
    for item in iter:
        template += '%s%s%s,' % (enclose, item, enclose)
    return template[:-1] + ")"





def column_names(cursor):
    return [column[0] for column in cursor.description]


# Creates an ordered dict object from a list of fields and a list of values.
def make_row_dict(fields, row):
    row_dict = {}
    for i in range(len(fields)):
        row_dict[fields[i]] = row[i]
    return row_dict