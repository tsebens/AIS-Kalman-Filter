from convert import make_state_from_deprecated_ais_data_format
from data import convert_ais_data_to_usable_form, convert_vsm_data_to_states, record_vms_data_by_vessel_id
from gen import gen_random_data, sin_1_4th
from estimation import default_location_estimate, est_head_max_turn_per_sec, est_SoG_max_spd_per_sec, \
    default_SoG_estimate, \
    default_heading_estimate, est_head_max_turn, est_loc_max_dis
from filter import ais_kalman
from plot import make_iterative_plot, plot
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

fp = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\ais_data\test_vms_data.csv'
print('Converting data to states')
states = convert_vsm_data_to_states(fp)
print('Running filter')
vessel_states = ais_kalman(states[1:], filter_state)
print('Making plot')
make_iterative_plot(vessel_states, delay=0.000000001)
input('Press enter')
