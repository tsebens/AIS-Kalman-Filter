import sys

from pypika import Table, Field

from connect import TableConnection, PostgreSQLDataBase
from vms import VMSDataPackage
from estimation import est_head_max_turn_per_sec, est_SoG_max_spd_per_sec, est_loc_max_dis, est_head_max_turn
from filter import ais_kalman
from prediction import default_SoG_prediction, default_heading_prediction, default_location_prediction
from state import FactorState, FilterState, FunctionState



factor_state = FactorState(
    loc_fact=0.5,
    head_fact=0.2,
    SoG_fact=0.2
)

location_functions = FunctionState(
    predict=default_location_prediction,
    estimate=est_loc_max_dis
)

heading_functions = FunctionState(
    predict=default_heading_prediction,
    estimate=est_head_max_turn_per_sec
)

SoG_functions = FunctionState(
    predict=default_SoG_prediction,
    estimate=est_SoG_max_spd_per_sec
)

filter_state = FilterState(
    factor_state,
    location_functions,
    heading_functions,
    SoG_functions
)

driver = '{PostgreSQL Unicode(x64)}'
server = 'localhost'
port = '6000'
dbname = 'kalman'
user = 'tristan.sebens'
pwd = ''

db_spec = PostgreSQLDataBase(server, port, dbname, user, pwd)

in_conn = db_spec.get_connection()
out_conn = db_spec.get_connection()
in_table = Table('VMS_TEST_VOYAGE')
out_table = Table("VMS_TEST_VOYAGE_FILTERED")
in_table_conn = TableConnection(in_conn, in_table, id_field=Field("VESSEL_ID"), id_value=2791)
out_table_conn = TableConnection(out_conn, out_table)
data_package = VMSDataPackage(in_tbl_conn=in_table_conn, out_tbl_conn=out_table_conn)
data_package.load_payload()
vessel_states = ais_kalman(data_package.get_states(), filter_state)
data_package.set_filtered_states(vessel_states)
data_package.write_payload()
in_conn.close()
out_conn.close()
