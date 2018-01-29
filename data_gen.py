from random import random
import math
import matplotlib.pyplot as plot

def x_noise():
    sign = -1
    if random() > .5:
        sign = 1
    return sign*(random()/2) # Returns a random value between -0.5 and 0.5

def y_noise(fact):
    sign = -1
    if random() > .5:
        sign = 1
    return sign * random() * fact # Returns a random value between -0.5 and 0.5

def gen_data(base_func, noise_fact, n):
    for i in range(n):
        x = i + x_noise()
        base = base_func(x)
        val = base + y_noise(noise_fact)
        yield (x, val)
