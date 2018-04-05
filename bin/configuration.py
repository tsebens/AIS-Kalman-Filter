'''
Configuration file.

Intended as a repository of constant variables and
configuration options that the user may want to change prior to running the application.


Note: NOT ALL OF THESE ARE ALWAYS USED
'''

# The maximum number of degrees the average fishing vessel is capable of turning per second.
# Used when estimating a vessel's heading.

MAX_ALLOWABLE_HEADING_CHANGE_DEGREES_PER_SECOND = .0000001

# Max speed of the average fishing vessel in m/s
MAX_ALLOWABLE_VESSEL_SPEED = 7.71667 # We'll set it at 15 knots, which is this (according to google)

# Max acceleration of the average fishing vessel
MAX_ALLOWABLE_VESSEL_ACCELERATION_METERS_PER_SECOND = 0.5

# Maximum number of degrees a vessel is allowed to change it's heading by between consecutive states
MAX_ALLOWABLE_TURN_PER_STATE = 25
'''
Constants
'''
# knts * knts_to_mps_conv_fact = m/s
knts_to_mps_conv_fact = 0.51444444444
