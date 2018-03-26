from datetime import timedelta, datetime
from random import random
import numpy as np
import math
import matplotlib.pyplot as plot

from timezones import Alaska


def sin_1_4th(x):
    return math.sin(x/4)


def noise(fact=1.0):
    sign = -1
    if random() > .5:
        sign = 1
    return sign*random()*fact # Returns a random value between -1.0 and 1.0 multiplied by the passed factor


'''
Generate semi noisy location ais_data based on a mathematical function
'''
def gen_loc_data(base_func, noise_fact, n):
    loc_data = []
    for i in range(n):
        x = i + noise(0.5)
        base = base_func(x)
        val = base + noise(noise_fact)
        loc_data.append(np.array([x, val]))
    return loc_data


'''
Generate semi noisy heading and SoG ais_data based on location ais_data
'''
def gen_head_and_SoG_data_from_loc(loc_data, noise_fact=0.1, display_vectors=False):
    prev = loc_data[0] # Get the initial state
    headings = []
    SoGs = []
    for curr in loc_data[1:]: # Skip the first location, because we've already stored it in prev
        delta_vector = np.subtract(curr, prev) # The exact change of location as a vector (curr-prev=delta)
        # The SoG is equal to the magnitude of the delta_vector,
        # and the heading is the unit vector form of the delta vector.
        SoG = np.linalg.norm(delta_vector)
        # Now we generate a 'noised' heading vector, which has been pushed in a random direction.
        # The magnitude of the noise introduced to the heading is within +/- noise_fact of the delta-vector magnitude
        # This ensures that the noise factor is always proportional to the delta-vector, no matter the heading's size.
        heading_noise = np.array([noise(SoG*noise_fact), noise(SoG*noise_fact)])
        # Now that we have both the delta-vector and the noise factor
        heading = np.add(delta_vector, heading_noise) # First add the heading noise to the delta vector
        heading = np.divide(heading, np.linalg.norm(heading)) # Then normalize the 'noised' heading vector into a unit vector
        # Now that we have the heading, introduce some noise into the SoG
        SoG = SoG + noise(SoG * noise_fact)  # Alter the SoG by +/- noise_fact of the original value
        headings.append(heading)
        SoGs.append(SoG)
        if display_vectors:
            plot_vectors(curr, prev, delta_vector, heading, heading_noise)
        prev = curr # Reset the pointers for the next iteration
    return headings, SoGs


def plot_vectors(curr, prev, delta_vector, heading, heading_noise):
    plot.scatter(curr[0], curr[1], color='r')
    plot.scatter(prev[0], prev[1], color='b')
    plot.pause(.5)
    plot_delta_vector(curr, delta_vector)
    plot_noise_vector(curr, heading_noise)
    plot_heading_vector(curr, heading)


def plot_heading_vector(curr, heading):
    plot.axes().quiver(curr[0], curr[1], heading[0], heading[1], angles='xy', scale_units='xy', scale=1, color='b')
    plot.pause(.5)


def plot_noise_vector(curr, heading_noise):
    plot.axes().quiver(curr[0], curr[1], heading_noise[0], heading_noise[1], angles='xy', scale_units='xy', scale=1,
                       color='k')
    plot.pause(.5)


def plot_delta_vector(curr, delta_vector):
    plot.axes().quiver(curr[0], curr[1], delta_vector[0], delta_vector[1], angles='xy', scale_units='xy', scale=1,
                       color='g')
    plot.pause(.5)


'''
Generate semi noisy ais ais_data, based on pre-generated location ais_data
'''
def gen_test_ais_data(loc_data, noise_fact=0.1):
    head_data, sog_data = gen_head_and_SoG_data_from_loc(loc_data, noise_fact)
    time = datetime.now(tz=Alaska)  # Grab the current time as a tz aware datetime object
    ais_data = []
    # We have to skip the last value, because there is exactly one fewer value for SoG and heading than there is for location
    for i in range(len(loc_data) - 1):
        ais_data.append(
            (loc_data[i], head_data[i], sog_data[i], time)
        )
        time += timedelta(seconds=5)  # Add five seconds to the time, the average time distance of AIS data points
    return ais_data


'''
Generate semi noisy ais ais_data, complete with location, heading, and SoG measurements, based on a mathematical function
'''
def gen_random_data(b_func=sin_1_4th, noise_fact=0.2, num_points=100):
    loc_data = gen_loc_data(b_func, noise_fact, num_points)
    return gen_test_ais_data(loc_data, noise_fact)

