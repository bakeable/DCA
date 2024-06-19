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
    alpha = self.warehouse.replenishments[index]
    S = self.warehouse.storage_capacities[index]
    w_i = self.warehouse.w_i
    v_i = self.warehouse.v_i

    # Assess local options

    assessed_options = []
    for option in local_options:
        new_n = n + option[0]
        new_k = k + option[1]

        option_distance = alpha * lookup_travel_distance(n, k, 1, S, w_i, v_i) + lookup_travel_distance(n, k, m, S, w_i, v_i)

        # Gather assessed option
        assessed_options.append((new_n, new_k, option_distance))

    # Sort by distance
    sorted_options = sorted(assessed_options, key=lambda tup: tup[2])

    # Apply best option
    n, k, distance = sorted_options[0]
    chromosome[self.N + index] = n
    chromosome[2 * self.N + index] = k

    return chromosome
