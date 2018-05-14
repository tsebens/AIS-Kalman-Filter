import sys
from os import getcwd, listdir
from os.path import join, splitext, basename

from plot import clear, show_plot
from calculate import rmse_of_states

cwd = getcwd()
sys.path.append(join(cwd, '..'))
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
    if count < 20:
        count += 1
        continue
    tv = TableVessel(db, vms_table, id_field, id_val)
    dp = VMSDataPackage(tv)
    dp.load_payload()
    states = dp.get_states()
    dp.set_filtered_states(ais_kalman(states, filter_state))
    rmse=rmse_of_states(states)
    make_plot(dp.get_filtered_states(), delay=0, title='RMSE: - %s ID - %s' % (rmse, id_val))
    show_plot()


'''
db = PostgreSQLDataBase(server, port, dbname, user, pwd, verbose=True)
db.test_connection()
in_table = INPUT_TABLE
out_table = OUTPUT_TABLE
ids = db.get_unique_elements(in_table, ID_FIELD)
for id in ids:
    in_table_vessel = TableVessel(db, in_table, id_field=ID_FIELD, id_value=id)
    out_table_vessel = TableVessel(db, out_table, id_field=ID_FIELD, id_value=id)
    data_package = VMSDataPackage(in_tbl_vessel=in_table_vessel, out_tbl_vessel=out_table_vessel)
    print("Loading values from DB")
    data_package.load_payload()
    print("Performing filter")
    data_package.set_filtered_states(ais_kalman(data_package.get_states(), filter_state))
    make_iterative_plot(data_package.get_filtered_states(), delay=0.1)
    input('Press enter to exit')
    sys.exit()
#data_package.write_payload()
'''
