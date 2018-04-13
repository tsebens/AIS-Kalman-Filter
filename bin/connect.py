from collections import OrderedDict
from typing import List

from pypyodbc import connect, Connection, Cursor

'''
Test db specs
driver = '{PostgreSQL Unicode(x64)}'
server = 'localhost'
port = '5433'
dbname = 'ais_kalman'
user = 'postgres'
pwd = 'postgres'
'''


class TableConnection():
    def __init__(self, conn: Connection, table_name: str):
        self.conn = conn
        self.tbl_name = table_name

    def init_connection(self):
        self.conn.connect()

    # Fills the data package with the relevant data from the database
    def get_data(self):
        return [row for row in retrieve_table_data(self.conn, self.tbl_name)]

    def write_data(self, data):
        write_table_data(self.conn, self.tbl_name, data)


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


def make_column_names_string(names):
    return enclose_values_in_parentheses(names, enclose='\"')


# Values must be a list of lists
def make_values_string(values: list):
    fieldnames = values[0].keys()
    return enclose_values_in_parentheses([enclose_values_in_parentheses([row[fieldnames] for fieldnames in fieldnames]) for row in values])


def make_insert_string(table: str, values: List[OrderedDict], schema: str=''):
    if schema != '':
        schema += '.'
    fieldnames = values[0].keys()
    template = 'INSERT INTO {schema}{table} {column_names} VALUES {values}'
    return template.format(schema=schema, table=table,
                           column_names=make_column_names_string(fieldnames),
                           values=make_values_string(values))


def make_truncate_string(table: str, schema: str=''):
    if schema != '':
        schema += '.'
    template = 'TRUNCATE {schema}{table}'
    return template.format(schema=schema, table=table)


def make_select_string(table, columns='*', where_str=None):
    if columns != '*':
        columns = enclose_values_in_parentheses(columns)
    template = "SELECT {columns} FROM {table}".format(columns=columns, table=table)
    if where_str is not None:
        template += ' ' + where_str
    return template


def column_names(cursor):
    return [column[0] for column in cursor.description]


# Creates an ordered dict object from a list of fields and a list of values.
def make_row_dict(fields, row):
    row_dict = {}
    for i in range(len(fields)):
        row_dict[fields[i]] = row[i]
    return row_dict


def retrieve_table_data(conn: Connection, table):
    cursor: Cursor = conn.cursor().execute(make_select_string(table))
    fields = column_names(cursor)
    for row in cursor:
        yield make_row_dict(fields, row)


def write_table_data(conn: Connection, table, data, truncate=True):
    cursor = conn.cursor()
    if truncate:
        cursor.execute(make_truncate_string(table))
    cursor.execute(make_insert_string(table, data))
    cursor.commit()
