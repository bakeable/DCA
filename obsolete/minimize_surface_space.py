from classes import Warehouse, PickingArea
from functions import read_instance
import itertools
import numpy as np
import math

# Read variables from instance
W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(2)

# Instantiate warehouse
warehouse = Warehouse(W, H, S, u, alpha, animate=True, w_i=w_i, v_i=v_i)


def minimize_surface_space(i):
    options = list(itertools.product(np.arange(warehouse.n_min[i],warehouse.n_max), np.arange(warehouse.k_min, warehouse.k_max)))
    optimal = (1, 2, math.inf)
    for option in options:
        # Unpack
        n, k = option

        # Instantiate picking area
        picking_area = PickingArea(S[i], n, k, u[i], alpha[i], w_i, v_i, i, "blue")

        # Get optimal
        if picking_area.surface < optimal[2]:
            optimal = (n, k, picking_area.surface)

    return optimal

# Get optimal choices
minimal_surface_spaces = []
for i in range(N):
    # Get minimal surface space
    minimal_surface_spaces.append(minimize_surface_space(i))

total_surface_needed = sum(x[2] for x in minimal_surface_spaces)
print("Warehouse has a surface of", warehouse.surface)
print("The total picking area surface is", total_surface_needed)
if total_surface_needed > warehouse.surface:
    print("The picking areas will not fit")


# Create chromosome
order = np.random.random_sample(N).round(2)
aisles = [x[0] for x in minimal_surface_spaces]
cross_aisles = [x[1] for x in minimal_surface_spaces]

# Test chromosome
warehouse.process([*order, *aisles, *cross_aisles])
warehouse.draw()
