'''
Configuration file.

Intended as a repository of constant variables and
configuration options that the user may want to change prior to running the application.

Note: NOT ALL OF THESE ARE ALWAYS USED
'''
# The number of degrees a fishing vessel can change it's heading by, per second

"""
--------------------------------------------------------------------------------------------
Static constants
--------------------------------------------------------------------------------------------
"""
AVERAGE_HEADING_CHANGE_DEGREES_PER_SECOND = 3
MAX_ALLOWABLE_HEADING_CHANGE_DEGREES_PER_SECOND = 0.001
# Maximum number of degrees a vessel is allowed to change it's heading by between consecutive states
MAX_ALLOWABLE_TURN_PER_STATE = 25

AVERAGE_VESSEL_SPEED = 3.85833 # 7.5 knots
MAX_ALLOWABLE_VESSEL_SPEED = 7.71667 # We'll set it at 15 knots, which is this (according to google)

# Max acceleration of the average fishing vessel
AVERAGE_VESSEL_ACCELERATION = 0.02
MAX_ALLOWABLE_VESSEL_ACCELERATION_METERS_PER_SECOND = 0.5

# A factor that is used to define the 'flexibility' of the rules imposed by the filter.
# The filter will define the outer limits of possibility as the calculated limit (according to the rules of the filter)
# multiplied
DEFAULT_GRACE_FACTOR = 1.25

# knts * knts_to_mps_conv_fact = m/s
KNTS_TO_MPS_CONV_FACT = 0.51444444444

# The directory where all grouped ais data will be stored
data_dir = r'C:\Users\tristan.sebens\Projects\AIS-Kalman-Filter\data'

# The directory where all downloaded OrbComm AIS data can be found
orbcomm_dir = r'C:\Users\tristan.sebens\Projects\OrbCommInterface\downloads'
