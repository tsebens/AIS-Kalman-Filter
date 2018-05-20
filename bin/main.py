import sys
from os import getcwd, listdir
from os.path import join, splitext, basename

from plot import clear, show_plot
from calculate import rmse_of_states

cwd = getcwd()
sys.path.append(join(cwd, '..'))
static_wd = r'F:\CIA_Python\PROD\PythonScripts\AIS-Kalman-Filter'
sys.path.append(static_wd) # We do this because SQL Server calls this script from a different working directory
sys.path.append(join(static_wd, 'bin'))
sys.path.append(join(static_wd, 'conf'))
from plot import make_iterative_plot, make_plot
from conf.db import server, port, dbname, user, pwd, ID_FIELD, OUTPUT_TABLE, INPUT_TABLE
from conf.filter import filter_state
from connect import TableVessel, SQLServerDataBase, PostgreSQLDataBase
from pypika import Table, Field
from vms import VMSDataPackage, CSV_VMSDataPackage
from filter import ais_kalman

vms_table = Table('STG_VMS', schema='dbo')
id_field = Field('VESSEL_ID')
db = SQLServerDataBase(server, port, dbname, '', '', trusted_source=True)
db.test_connection()
ids = db.get_unique_elements(vms_table, id_field)
count = 0
for id_val in ids:
    try:
        print('Processing %s' % id)
        in_tbl_vessel = TableVessel(db, INPUT_TABLE, id_field=ID_FIELD, id_value=id_val)
        out_tbl_vessel = TableVessel(db, OUTPUT_TABLE, id_field=ID_FIELD, id_value=id_val)
        data_package = VMSDataPackage(in_tbl_vessel, out_tbl_vessel)
        data_package.load_payload()
        data_package.set_filtered_states(ais_kalman(data_package.get_states(), filter_state))
        data_package.write_payload()
    except StopIteration:
        print('Empty dataset')
        continue