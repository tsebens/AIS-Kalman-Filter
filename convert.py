# Logic class for any conversions that need to be made
from math import tan, radians
import numpy as np
from datetime import datetime
from timezones import UTC


# Converts a true heading to a unit vector
def true_heading_to_unit_vector(point):
    unit_v = np.array([1, tan(radians(point[['True_heading']]))])
    mag = np.linalg.norm(unit_v)
    unit_v = unit_v/mag
    unit_v = np.array([unit_v[1], unit_v[0]])
    return unit_v

# TODO: Convert a timestamp of format [2/26/2018 12:03:59] to a datetime object
def ais_timestamp_to_datetime(timestamp, tz=UTC):
    date, time = timestamp.split(' ')
    year, month, day = date.split('-')
    hour, minute, second = time.split(':')
    return datetime(day=int(day), month=int(month), year=int(year), hour=int(hour), minute=int(minute), second=int(second), tzinfo=tz)


def lat_lon_to_loc_vector(point, lat_fn='AA_LAT', lon_fn='AA_LON'):
    aa_lat = point[lat_fn]
    aa_lon = point[lon_fn]
    return np.array([aa_lat, aa_lon])


def sog(point, sog_fn='SOG__knts_'):
    return point[sog_fn]