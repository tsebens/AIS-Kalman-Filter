# Kalman filter
import numpy as np

from estimation import default_SoG_estimate, defalt_heading_estimate, default_location_estimate

'''
Executes a Kalman filter on the passed ais_data and returns a list of estimates for location(lat/lon), heading, and SoG for every point in ais_data after the first.
The first point is considered to be completely accurate. Gotta start somewhere.
Data is an nx4 numpy array, each row of which == (loc, heading, SoG, time)
loc must be a numpy array, representing Lat/Lon (lat, lon)
Heading must be a unit vector (length 1), and must come in as a numpy array (lat, lon)
SoG must be in DecDeg/sec
time must be an aware datetime object (timezone aware)
loc_, head_, and SoG_ fact's' represent the consideration factors for each value. Essentially a measure of the proportion 
of the final estimate that will be made up of the measurement. 
A high fact will result in a higly influential measurement: 
the final estimates will be very faithful to the measurements. 
A low fact will result in a very uninfluential measurement: 
the final estimates will be far more closely tied to the predictions made prior to the estimates.

In simpler terms, think of fact as a metric of how trustworthy a set of measurements are: A low fact is good for 
measurements that are error prone. A high fact is good for measurements that tend to be accurate.

The prediction and estimation functions are used to provide the predictions and the estimates for the new values 
of the location, heading, and speed, based on the relevant previous values.
By defining these as passed functions with default values, it becomes possible to inject the logi which 
the filter uses to make it's predictions and estimates.
'''
def ais_kalman(data, loc_fact=0.5, head_fact=0.5, SoG_fact=0.5,
               est_location_func=default_location_estimate,  # Functions used to estimate filter values
                est_heading_func=defalt_heading_estimate,
                    est_SoG_func=default_SoG_estimate):
    # Initialize our lists for storing the results of the filter
    loc_predictions, head_predictions, SoG_predictions, loc_estimates, head_estimates, SoG_estimates = [], [], [], [], [], []
    # Populate our initial values
    init = data[0]
    # loc_est is a vector of the form (x,y) or (lon, lat) that indicates the vessels current location in Alaska Albers coordinates
    # head_est is a unit vector (length = 1) of the form (x,y) which indicates the vessel's current heading in Alaska Albers coordinates
    # SoG is a vectorless float value indicating the vessels's speed in m/s
    loc_est, head_est, SoG_est, prev_time = init[0], init[1], init[2], init[3]
    # Now, for every data point we have (skipping the first one since we've already loaded those values) we use the
    # Kalman filter to estimate the true location of our vessel.
    for row in data[1:]:
        # These represent the values held by the data point we are currently considering
        loc_meas, head_meas, SoG_meas, time_meas = row[0], row[1], row[2], row[3]
        # Next calculate how much time has passed since the last reading
        calculate_seconds_passed(prev_time, time_meas)

        # TODO: The modularity and flexibility of this filter can be improved here -->
        '''
        By refactoring this step into a function that is passed into the filter as a parameter. So rather than 
        calculating our predictions here, we would simply call the function that had been given to us which 
        would take our loc, head, and SoG estimates as parameters, and return a loc, head, and SoG predictions.
        '''
        # Now we can make our predictions for location, heading, and SoG
        # (x0, y0)+(xHead, yHead)*SoG*dt
        # The previous location estimate plus the amount of distance they would cover at the estimated speed in the time
        # that passed. Multiplied by the unit vector representing our estimated heading. Simple vector addition
        loc_pred = np.add(loc_est, head_est*SoG_est)
        head_pred = head_est  # We assume that vessels maintain their heading over time.
        SoG_pred = SoG_est    # We assume that vessels maintain their speed over time.

        # Log our predictions into their appropriate containers
        loc_predictions.append(loc_pred)
        head_predictions.append(head_pred)
        SoG_predictions.append(SoG_pred)

        # Now that we have all of our predictions, we will compare them to our measurements, and create our new estimates.
        loc_est = est_location_func(loc_fact, loc_meas, loc_pred)
        head_est = est_heading_func(head_fact, head_meas, head_pred)
        SoG_est = est_SoG_func(SoG_fact, SoG_meas, SoG_pred)
        # Log out estimates into their containers
        loc_estimates.append(loc_est)
        head_estimates.append(head_est)
        SoG_estimates.append(SoG_est)

    return loc_estimates, loc_predictions, head_estimates, head_predictions, SoG_estimates, SoG_predictions


def calculate_seconds_passed(prev_time, time_meas):
    time_passed = time_meas - prev_time
    prev_time = time_meas  # Reset the time for the next iteration
    seconds_passed = time_passed.total_seconds()  # Get the value in seconds. This will probably be useful. Someday. Hopefully.






