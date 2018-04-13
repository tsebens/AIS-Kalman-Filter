from connect import TableConnection, connect_to_db
from data import VMSDataPackage
from estimation import est_head_max_turn_per_sec, est_SoG_max_spd_per_sec, est_loc_max_dis, est_head_max_turn
from filter import ais_kalman
from plot import make_iterative_plot
from prediction import default_SoG_prediction, default_heading_prediction, default_location_prediction
from state import FactorState, FilterState, FunctionState
from pypyodbc import connect



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
port = '5433'
dbname = 'ais_kalman'
user = 'postgres'
pwd = 'postgres'

conn = connect_to_db(driver, server, port, dbname, user, pwd)
in_table = 'vms_test_voyage'
out_table = 'vms_test_voyage_filtered'
in_table_conn = TableConnection(conn, in_table)
out_table_conn = TableConnection(conn, out_table)
print('Converting data to states')
data_package = VMSDataPackage(in_tbl_conn=in_table_conn, out_tbl_conn=out_table_conn)
print('Loading data from DB')
data_package.load_payload()
print('Running filter')
vessel_states = ais_kalman(data_package.get_states(), filter_state)
data_package.set_filtered_states(vessel_states)
data_package.write_payload()
conn.close()
