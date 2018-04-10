'''
Configuration file.

Intended as a repository of constant variables and
configuration options that the user may want to change prior to running the application.


Note: NOT ALL OF THESE ARE ALWAYS USED
'''
# The number of degrees a fishing vessel can change it's heading by, per second
AVERAGE_HEADING_CHANGE_DEGREES_PER_SECOND = 3
MAX_ALLOWABLE_HEADING_CHANGE_DEGREES_PER_SECOND = 6
# Maximum number of degrees a vessel is allowed to change it's heading by between consecutive states
MAX_ALLOWABLE_TURN_PER_STATE = 25

AVERAGE_VESSEL_SPEED = 3.85833 # 7.5 knots
MAX_ALLOWABLE_VESSEL_SPEED = 7.71667 # We'll set it at 15 knots, which is this (according to google)

# Max acceleration of the average fishing vessel
AVERAGE_VESSEL_ACCELERATION = 0.02
MAX_ALLOWABLE_VESSEL_ACCELERATION_METERS_PER_SECOND = 0.5


'''
Constants
'''
# knts * knts_to_mps_conv_fact = m/s
knts_to_mps_conv_fact = 0.51444444444
