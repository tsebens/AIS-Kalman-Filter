import sys
import os
import os.path
sys.path.append(os.path.join(os.getcwd(), '..'))

from pypika import Table, Field
from conf.db import server, port, dbname, user, pwd, ID_FIELD, OUTPUT_TABLE, INPUT_TABLE
from conf.filter import filter_state
from connect import TableVessel, PostgreSQLDataBase, SQLServerDataBase
from vms import VMSDataPackage
from filter import ais_kalman

db = SQLServerDataBase(server, port, dbname, user, pwd)
in_table = INPUT_TABLE
out_table = OUTPUT_TABLE
ids = db.get_unique_elements(in_table, ID_FIELD)
in_table_vessel = TableVessel(db, in_table, id_field=ID_FIELD, id_value=2791)
out_table_vessel = TableVessel(db, out_table, id_field=ID_FIELD, id_value=2791)
data_package = VMSDataPackage(in_tbl_vessel=in_table_vessel, out_tbl_vessel=out_table_vessel)
data_package.load_payload()
vessel_states = ais_kalman(data_package.get_states(), filter_state)
data_package.set_filtered_states(vessel_states)
#make_iterative_plot(data_package.get_filtered_states(), delay=0.00001)
data_package.write_payload()
