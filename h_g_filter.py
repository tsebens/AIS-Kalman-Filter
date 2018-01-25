# Kalman filter
import numpy as np
'''
Executes a Kalman filter on the passed data and returns a list of estimates for location(lat/lon), heading, and SoG for every point in data after the first.
The first point is considered to be completely accurate. Gotta start somewhere.
Data is an nx4 numpy array, each row of which == (loc, heading, SoG, time)
loc must be a numpy array, representing Lat/Lon (lat, lon)
Heading must be a unit vector (length 1), and must come in as a numpy array (lat, lon)
SoG must be in DecDeg/sec
time must be an aware datetime object (timezone aware)
loc_, head_, and SoG_ fact's' represent the consideration factors for each value. Essentially a measure of the proportion of the final estimate that will be made up of the measurement. A high fact will result in a higly influential measurement: the final estimates will be very faithful to the estimates. A low fact will result in a very uninfluential measurement: the final estimates will be far more closely tied to the predictions made prior to the estimates.

In simpler terms, think of the fact as a metric of how trustworthy a set of measurements are: A low fact is good for measurements that are error prone. A high fact is good for measurements that tend to be accurate.
'''
def ais_kalman(data, loc_fact, head_fact, SoG_fact):
	# Populate our initial values
	init = data[0]
	loc_est, head_est, SoG_est, prev_time = init[1], init[2], init[3], init[4]	
	estimates = []
	
	for row in data[1:]:
		# These represent the values held by the data point we are currently considering
		loc_meas, head_meas, SoG_meas, time_meas = row[0], row[1], row[2], row[3]
		# Next calculate how much time has passed since the last reading
		time_passed = meas_time - prev_time
		seconds_passed = time_passed.total_seconds() # Get the value in seconds
		# Now we can make our predictions for location, heading, and SoG
		# (x0, y0)+(xHead, yHead)*SoG*dt # The previous location estimate plus the amount of distance they would cover at the estimated speed in the time that passed. Multiplied by the unit vector representing our estimated heading. Simple vector addition
		loc_pred = np.add(loc_est, head_est*SoG_est*seconds_passed)
		head_pred = head_est # We assume that vessels maintain their heading over time.
		SoG_pred = SoG_est # We assume that vessels maintain their speed over time
		# Now that we have all of our predictions, we will compare them to our measurements, and create our new estimates.
		loc_est = np.add(loc_pred, loc_fact*loc_meas)
		head_est = np.add(head_pred, head_fact*head_meas)
		SoG_est = SoG_pred+SoG_fact*SoG_meas
		estimates.append(loc_est, head_est, SoG_est, time_meas)
	return estimates
		
		
