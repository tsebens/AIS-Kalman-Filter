from connect import TableConnection
from data import VMSDataPackage
from estimation import est_head_max_turn_per_sec, est_SoG_max_spd_per_sec, est_loc_max_dis, est_head_max_turn
from filter import ais_kalman
from plot import make_iterative_plot
from prediction import default_SoG_prediction, default_heading_prediction, default_location_prediction
from state import FactorState, FilterState, FunctionState

driver = '{PostgreSQL Unicode(x64)}'
server = 'localhost'
port = '5433'
dbname = 'ais_kalman'
user = 'postgres'
pwd = 'postgres'


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

table_conn = TableConnection('vms_test_voyage', driver, server, port, dbname, user, pwd)
table_conn.init_connection()
print('Converting data to states')
data_package = VMSDataPackage(table_conn)
print('Loading data from DB')
data_package.load_payload()
print('Running filter')
vessel_states = ais_kalman(data_package.get_states(), filter_state)
print('Making plot')
make_iterative_plot(vessel_states, delay=0.000000001)
input('Press enter')
