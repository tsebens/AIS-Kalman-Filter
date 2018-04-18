from pypika import Table
from conf.db import server, port, dbname, user, pwd
from conf.filter import filter_state
from connect import TableVessel, PostgreSQLDataBase
from db import ID_FIELD, OUTPUT_TABLE, INPUT_TABLE
from vms import VMSDataPackage
from filter import ais_kalman

db = PostgreSQLDataBase(server, port, dbname, user, pwd)

in_table = Table(INPUT_TABLE)
out_table = Table(OUTPUT_TABLE)
ids = db.get_ids(in_table, ID_FIELD)
conn = db.get_connection()
in_table_vessel = TableVessel(conn, in_table, id_field=ID_FIELD, id_value=2791)
out_table_vessel = TableVessel(conn, out_table, id_field=ID_FIELD, id_value=2791)
data_package = VMSDataPackage(in_tbl_vessel=in_table_vessel, out_tbl_vessel=out_table_vessel)
data_package.load_payload()
vessel_states = ais_kalman(data_package.get_states(), filter_state)
data_package.set_filtered_states(vessel_states)
#make_iterative_plot(data_package.get_filtered_states(), delay=0.00001)
data_package.write_payload()
conn.close()
