import sys
from os import getcwd
from os.path import join

cwd = getcwd()
sys.path.append(join(cwd, '..'))
from plot import make_iterative_plot
from conf.db import server, port, dbname, user, pwd, ID_FIELD, OUTPUT_TABLE, INPUT_TABLE
from conf.filter import filter_state
from connect import TableVessel, SQLServerDataBase, PostgreSQLDataBase
from vms import VMSDataPackage
from filter import ais_kalman

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
    vessel_states = ais_kalman(data_package.get_states(), filter_state)
    data_package.set_filtered_states(vessel_states)
    make_iterative_plot(data_package.get_filtered_states(), delay=.2)
    input('Press enter to exit')
    sys.exit()
#data_package.write_payload()
