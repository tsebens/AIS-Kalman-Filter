from calculate import angle_between, rotate_vector, vector_between_two_points, vector_length, unit_vector
from conf.static import MAX_ALLOWABLE_HEADING_CHANGE_DEGREES_PER_SECOND, \
    MAX_ALLOWABLE_VESSEL_ACCELERATION_METERS_PER_SECOND, MAX_ALLOWABLE_TURN_PER_STATE, MAX_ALLOWABLE_VESSEL_SPEED
from convert import make_est_from_meas_pred_and_fact, seconds_passed_between_states
from state import VesselState, FilterState
from conf.static import DEFAULT_GRACE_FACTOR
from numpy import add, multiply

'''
The estimation step is where we combine what we predicted about the state of the vessel with what we measured, and do so 
in an intelligent and intentional manner.
'''


'''
IMPORTANT: ALL FUNCTION GROUPS MUST HAVE THE SAME DEFAULT FUNCTION SIGNATURE
Additional named variables are okay as long as they have default values
All functions should have a uniform function signature, where all parameters have the same name, and the same order
In addition, all parameters should be given empty default values. This way, any function that is called will simply 
have the relevant parameters overridden
'''

'''
The default functions for estimating 
'''
def default_SoG_estimate(filter_state: FilterState, curr_state: VesselState, prev_state: VesselState):
    SoG_fact = filter_state.factors.SoG_factor
    return make_est_from_meas_pred_and_fact(curr_state.SoG_state.meas,
                                            curr_state.SoG_state.pred,
                                            SoG_fact)


def default_heading_estimate(filter_state: FilterState, curr_state: VesselState, prev_state: VesselState):
    head_fact = filter_state.factors.heading_factor
    return make_est_from_meas_pred_and_fact(curr_state.head_state.meas,
                                            curr_state.head_state.pred,
                                            head_fact)


def default_location_estimate(filter_state: FilterState, curr_state: VesselState, prev_state: VesselState):
    loc_fact = filter_state.factors.location_factor
    return make_est_from_meas_pred_and_fact(curr_state.loc_state.meas,
                                            curr_state.loc_state.pred,
                                            loc_fact)


# Returns the SoG estimate, but caps the estimate under the rule that the vessel cannot gain more than
# max_acc knts per second of acceleration. It is assumed that a boat can lose speed as quickly as it likes.
def est_SoG_max_spd_per_sec(filter_state:FilterState, curr_state:VesselState, prev_state:VesselState,
                            max_acc=MAX_ALLOWABLE_VESSEL_ACCELERATION_METERS_PER_SECOND, grace_fact=DEFAULT_GRACE_FACTOR):
    time_passed = curr_state.timestamp - prev_state.timestamp
    max_spd_change = max_acc * time_passed.total_seconds()
    meas_speed = curr_state.SoG_state.meas

    default = max(default_SoG_estimate(filter_state, curr_state, prev_state), 0)
    max_change = max((prev_state.SoG_state.est + max_spd_change) * grace_fact, 0)

    return min(default, max_change)


# Estimate the new heading based on the prediction, and the measurement, but with the rule that the
# heading can only change so fast.
def est_head_max_turn_per_sec(filter_state:FilterState, curr_state:VesselState, prev_state:VesselState,
                              max_turn=MAX_ALLOWABLE_HEADING_CHANGE_DEGREES_PER_SECOND, grace_fact=DEFAULT_GRACE_FACTOR):
    total_seconds = seconds_passed_between_states(curr_state, prev_state)
    max_head_change = (max_turn * total_seconds) * grace_fact
    # First we make our usual estimate, then we compare that to our rules.
    pred_heading = default_heading_estimate(filter_state, curr_state, prev_state)
    # If the predicted heading would exceed the allowable heading change,
    # then use the max heading change value instead
    if angle_between(prev_state.head_state.est, pred_heading) > max_head_change:
        # This next part is actually sort of a work around. I don't know mathematically how to
        # derive the heading unit vector, because there are two possible values. I calculate
        # them both here, then determine which one is the better answer.
        v1 = rotate_vector(prev_state.head_state.est, max_head_change)
        v2 = rotate_vector(prev_state.head_state.est, -1 * max_head_change)
        if angle_between(v1, pred_heading) < angle_between(v2, pred_heading):
            # v1 is closer to the predicted heading than v1, which means its the appropriate estimation
            return v1
        else:
            return v2
    else:
        # If we reach this point, then the predicted heading is within allowable tolerances.
        return pred_heading


# Enforces a rule that the boat's location cannot change more than is mathematically possible based on
# it's course and speed.
# The grace factor is a measure of how flexible we are willing to be with this rule
# If, for example, the grace factor is 1.5, then a distance which is less than or equal to
# 1.5 times the expected distance would be considered acceptable
def est_loc_max_dis(filter_state: FilterState, curr_state: VesselState, prev_state: VesselState,
                    max_speed=MAX_ALLOWABLE_VESSEL_SPEED, grace_fact=DEFAULT_GRACE_FACTOR):
    # First we get our default estimation, then we compare that to our rules
    est_location = default_location_estimate(filter_state, curr_state, prev_state)
    # Now we get the vector between our new estimate and our estimated location from the previous state
    delta_v = vector_between_two_points(prev_state.loc_state.est, est_location)
    # The length of delta_v represents the distance we travelled
    distance = vector_length(delta_v)
    # This is the crux of it. If this distance is too large, then we have to intervene.
    # First we calculate our max allowable distance
    total_seconds = seconds_passed_between_states(curr_state, prev_state)
    max_allowable_distance = max_speed * total_seconds * grace_fact
    if distance > max_allowable_distance:
        # The default estimate violates the rule's constraints. We have to recalculate a value that is within our bounds
        # We calculate a new estimated location, which is equal to where the boat would have been if it
        # maintained it's course, and moved the maximum allowable distance.
        # First we need to find the unit vector from our current location to the estimate
        dir_to_est = unit_vector( # todo: Figure out why this has to be inverted. It doesn't work without it.
            vector_between_two_points(
                est_location,
                prev_state.loc_state.est
            )
        )
        est_location = prev_state.loc_state.est + dir_to_est * max_allowable_distance
    return est_location


# Similar to est_head_max_turn_per_sec, except this function does not consider the time passed. According to
# this estimation function, the vessel is not capable of turning more that max_turn degrees between states,
# irregardless of the amount of time that has passed.
def est_head_max_turn(filter_state:FilterState, curr_state: VesselState, prev_state: VesselState, max_turn=MAX_ALLOWABLE_TURN_PER_STATE):
    max_head_change = max_turn
    # First we make our usual estimate, then we compare that to our rules.
    est_heading = default_heading_estimate(filter_state, curr_state, prev_state)
    # If the predicted heading would exceed the allowable heading change,
    # then use the max heading change value instead
    if angle_between(prev_state.head_state.est, est_heading) > max_head_change:
        # This next part is actually sort of a work around. I don't know mathematically how to
        # derive the heading unit vector, because there are two possible values. I calculate
        # them both here, then determine which one is the better answer.
        v1 = rotate_vector(prev_state.head_state.est, max_head_change)
        v2 = rotate_vector(prev_state.head_state.est, -1 * max_head_change)
        if angle_between(v1, est_heading) < angle_between(v2, est_heading):
            # v1 is closer to the predicted heading than v1, which means its the appropriate estimation
            return v1
        else:
            return v2
    else:
        # If we reach this point, then the predicted heading is within allowable tolerances.
        return est_heading


def est_loc_ignore_heading_max_distance(filter_state: FilterState, curr_state: VesselState, prev_state: VesselState,
       max_speed=MAX_ALLOWABLE_VESSEL_SPEED):
    # We put our estimate on the measured location of this point
    est_location = curr_state.loc_state.meas
    # Now we get the vector between our new estimate and our estimated location from the previous state
    delta_v = vector_between_two_points(prev_state.loc_state.est, est_location)
    # The length of delta_v represents the distance we travelled
    distance = vector_length(delta_v)
    # This is the crux of it. If this distance is too large, then we have to intervene.
    # First we calculate our max allowable distance
    total_seconds = seconds_passed_between_states(curr_state, prev_state)
    max_allowable_distance = max_speed * total_seconds
    if distance > max_allowable_distance:
        # The default estimate violates the rule's constraints. We have to recalculate a value that is within our bounds
        # We calculate a new estimated location, which is equal to where the boat would have been if it
        # maintained it's course, and moved the maximum allowable distance.
        # First we need to find the unit vector from our current location to the estimate
        dir_to_est = unit_vector(  # todo: Figure out why this has to be inverted. It doesn't work without it.
            vector_between_two_points(
                est_location,
                prev_state.loc_state.est
            )
        )
        est_location = add(prev_state.loc_state.est, multiply(dir_to_est, max_allowable_distance))
    return est_location



