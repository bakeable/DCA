from classes import Warehouse, PickingArea, GeneticAlgorithm
from functions import read_instance
import itertools
import numpy as np
import math
from random import random, randrange
from copy import copy

def calculate_total_surface(picking_areas):
    if len(picking_areas) == 0:
        return math.inf

    # Instantiate surface
    surface = 0

    # Add surface of every area
    for picking_area in picking_areas:
        surface = surface + picking_area.surface

    return surface

# Read variables from instance
W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(2)

# Instantiate warehouse
algorithm = GeneticAlgorithm()
algorithm.instantiate(2)
warehouse = algorithm.warehouse
warehouse.reset()

# n,k combinations
options = list(itertools.product(np.arange(1, warehouse.n_max), np.arange(2, warehouse.k_max)))

picking_areas = []
min_chromosome = None
min_surface = math.inf
it = 0
while calculate_total_surface(picking_areas) > warehouse.surface and it < 1000:
    it = it + 1

    # Create chromosome
    chromosome = algorithm.create_random_chromosome()
    order = chromosome[:N]
    aisles = chromosome[N:(2 * N)]
    cross_aisles = chromosome[(2 * N):(3 * N)]

    # Create picking areas
    for index in range(N):
        # Get number of aisles, cross-aisles, storage capacity, order distribution and replenishment constant
        n = aisles[index]
        k = cross_aisles[index]
        s_i = warehouse.storage_capacities[index]
        m = warehouse.order_sizes[index]
        alpha = warehouse.replenishments[index]
        color = warehouse.PA_colors[index]

        # Create picking area
        picking_area = PickingArea(s_i, n, k, m, alpha, warehouse.w_i, warehouse.v_i, index, color)

        # Append
        picking_areas.append(picking_area)

    if calculate_total_surface(picking_areas) < min_surface:
        min_chromosome = chromosome

if it == 1000:
    chromosome = min_chromosome

print("Best chromosome found", chromosome)

def process_picking_areas():
    # Reset warehouse
    warehouse.reset()
    bottleneck = None
    changes = []
    for picking_area in picking_areas:
        # Insert picking area
        warehouse.insert_picking_area(picking_area)

        # Draw
        warehouse.draw(True)

        # If not feasible, try all options
        if not warehouse.feasible:
            # Try all options for selected picking area
            feasibility_changes = []
            surface_space_left = warehouse.get_total_ems()
            print("Starting options")
            for option in options:
                # Remove last picking area
                warehouse.remove_infeasible_picking_areas()

                # Get new option
                n, k = option
                picking_area.set_parameters(n, k)

                # Place under minor restrictions
                if picking_area.surface <= surface_space_left and picking_area.w <= warehouse.W and picking_area.h <= warehouse.H:
                    # Create copy
                    warehouseCopy = copy(warehouse)

                    # Place in the copy
                    warehouseCopy.feasible = True
                    warehouseCopy.insert_picking_area(picking_area)

                    # Draw
                    warehouseCopy.draw(True)

                    # Save frame files
                    warehouse.frame = warehouseCopy.frame
                    warehouse.frame_files = warehouseCopy.frame_files

                    # Save all possible changes that make it feasible
                    if warehouseCopy.feasible:
                        feasibility_changes.append(
                            (picking_area.n, picking_area.k, warehouseCopy.total_travel_distance, picking_area.surface))

                print("Stuck in options?")

            # Possible changes to chromosome
            changes.append(feasibility_changes)

            # If there is a feasible option, place it
            if len(feasibility_changes) > 0:
                # Get best option based on surface or objective value or their product
                n, k, obj_value, surface = sorted(feasibility_changes, key=lambda tup: tup[2] * tup[3])[randrange(0, round(N/2))]
                picking_area.set_parameters(n, k)

                # Insert feasible picking area
                warehouse.insert_picking_area(picking_area)
                warehouse.feasible = True

                # Draw
                warehouse.draw(True)

                print("Feasible changes?")

            # Calculate the option with the least surface
            else:
                # Surfaces
                surface_options = []
                for option in options:
                    # Get parameters
                    n, k = option

                    # Set parameters
                    picking_area.set_parameters(n, k)

                    # Save surface and parameters
                    surface_options.append((n, k, picking_area.surface))

                # Set parameters to smallest
                n, k, surface = sorted(surface_options, key=lambda tup: tup[2])[randrange(0, round(N/2))]

                # Set parameters
                picking_area.set_parameters(n, k)

                # Set bottleneck
                bottleneck = picking_area.number

                print("Looping?")

        else:
            # No changes to chromosome
            changes.append(None)

        print("Finished picking area")

    print("No solution found")
    return bottleneck


bottleneck = process_picking_areas()
while bottleneck is not None:
    # Move last picking area to first
    if random() < 1:
        new_order = [N-1, *range(N-1)]
    else:
        new_order = np.argsort(np.random.random_sample(N).round(2))
    print(new_order)
    picking_areas = np.array(picking_areas)
    picking_areas = picking_areas[new_order]

    bottleneck = process_picking_areas()


# Create animation
warehouse.chromosome = "test"
warehouse.create_animation(3)