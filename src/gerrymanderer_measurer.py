from electorate import Electorate
from gerrymanderer import *
from striper import Striper

def measure(d, n, gerrymanderer):
    """
    Returns the average measurement over n d * d electorates
    :param d: Number of districts (and also number of voters per district)
    :param n: Number of simulations to run
    :param gerrymanderer: An object with a gerrymander method
    :return: A number between 0.0 (losing every district) and 1.0 (winning every district).
    """
    sum = 0
    for i in range(n):
        e = Electorate(d)
        for party in [False, True]:
            districts = gerrymanderer.gerrymander(e, party)
            if not e.is_valid_map(districts):
                raise ValueError('Invalid districts')
            sum += e.get_wins(districts, party)
    return sum / (d * 2 * n)

# 12 max, 13 is cooked
width = 9
simulations = 1
e = Electorate(width)
gr = Grid(width)

import time

start_time = time.time()

print(measure(width, simulations, Gerrymanderer(gr)))
print(measure(width, simulations, Striper()))
# Code to be timed
end_time = time.time()
elapsed_time = end_time - start_time
print("Elapsed time:", elapsed_time)
