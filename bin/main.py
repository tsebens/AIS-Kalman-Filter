from convert import make_state_from_deprecated_ais_data_format
from gen import gen_random_data, sin_1_4th
from estimation import default_SoG_estimate, default_location_estimate, defalt_heading_estimate, est_head_max_turn, \
    est_SoG_max_spd
from h_g_filter import ais_kalman
from plot import make_iterative_plot
from prediction import default_SoG_prediction, default_heading_prediction, default_location_prediction
from state import FactorState, FilterState, FunctionState

loc_fact = 0.2
head_fact = 0.4
SoG_fact =0.4

factor_state = FactorState(
    loc_fact=0.5,
    head_fact=0.2,
    SoG_fact=0.2
)

location_functions = FunctionState(
    predict=default_location_prediction,
    estimate=default_location_estimate
)

heading_functions = FunctionState(
    predict=default_heading_prediction,
    estimate=est_head_max_turn
)

SoG_functions = FunctionState(
    predict=default_SoG_prediction,
    estimate=est_SoG_max_spd
)

filter_state = FilterState(
    factor_state,
    location_functions,
    heading_functions,
    SoG_functions
)

data = gen_random_data()
states = [make_state_from_deprecated_ais_data_format(point) for point in data]
vessel_states = ais_kalman(states, filter_state)
make_iterative_plot([state.loc_state for state in vessel_states], b_func=sin_1_4th)
input('Press enter')
