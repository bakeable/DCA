import numpy as np
from random import choice


# Calculates options for the aisles that might be optimal, such that it divides the warehouse in an integer number of width
def mutate_008(self, chromosome):
    # Aisle options
    max_n = self.warehouse.n_max
    divisible_by = []
    for x in range(2, max_n):
        if max_n % x == 0:
            divisible_by.append(x)
    aisle_options = max_n / np.array(divisible_by)

    # Choose one of the preferred aisle options
    if len(aisle_options) > 0:
        chromosome[1 * self.N:2 * self.N] = [choice(aisle_options) for x in range(self.N)]

    return chromosome
