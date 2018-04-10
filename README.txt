AIS Kalman filter

Developed for NMFS by Tristan Sebens
tristan.ng.sebens@gmail.com
907-500-5430

This intent of this application is to process marine gps sensor data which is assumed to be relatively noisy and
inaccurate, and to estimate the likely path of the vessel based on both the incoming data and a set of defined
rules which are intended to model the manner in which a vessel typically behaves.

For example:
Assume you have two sequential gps readings, which are 5 seconds apart, and about 100m apart. This implies that
the vessel moved, on average, 20m/s between those two points. However, what if we know that this vessel is in
fact incapable of moving more than 12m/s? We can safely assume that the readings are erroneous, and we can
adjust our estimation of where the vessel actually is accordingly.

Similarly, if the heading measurement for a vessel changes by 30 degrees in just 2 seconds, but we know that
the vessel is incapable of turning faster than 5 degrees/second, we can adjust our estimation of the boats behaviour
accordingly.