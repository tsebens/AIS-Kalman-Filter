from connect import get_states_from_table_data
from data import convert_vsm_data_to_states
from estimation import est_head_max_turn_per_sec, est_SoG_max_spd_per_sec, est_loc_max_dis
from filter import ais_kalman
from plot import make_iterative_plot
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

print('Converting data to states')
states = get_states_from_table_data('vms_test_voyage')
print('Running filter')
vessel_states = ais_kalman(states[1:], filter_state)
print('Making plot')
make_iterative_plot(vessel_states, delay=0.000000001)
input('Press enter')
