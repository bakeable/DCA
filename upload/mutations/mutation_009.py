import numpy as np
from random import choice, randrange
from functions import lookup_travel_distance
import itertools


# Calculates options for the aisles that might be optimal, such that it divides the warehouse in an integer number of width
def mutate_009(self, chromosome):
    # Optimize one picking area locally for both aisle and cross-aisle
    local_options = itertools.permutations([-1, 0, 1], 2)

    # Get random picking area index
    index = randrange(0, self.N)

    # Get current n and k
    n, k = chromosome[self.N + index], chromosome[2 * self.N + index]

    # Get picking area order distribution
    m = self.warehouse.order_sizes[index]

    # Assess local options

    assessed_options = []
    for option in local_options:
        new_n = n + option[0]
        new_k = k + option[1]

        option_distance = lookup_travel_distance(new_n, new_k, m)

        # Gather assessed option
        assessed_options.append((new_n, new_k, option_distance))

    # Sort by distance
    sorted_options = sorted(assessed_options, key=lambda tup: tup[2])

    # Apply best option
    n, k, distance = sorted_options[0]
    chromosome[self.N + index] = n
    chromosome[2 * self.N + index] = k

    return chromosome
