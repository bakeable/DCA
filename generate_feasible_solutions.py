from classes import Warehouse, PickingArea
from functions import read_instance
import itertools
import numpy as np
import math
from random import random, randrange, shuffle, sample
from copy import copy
from functions.data_handling import get_instances
from tqdm import tqdm
from datetime import datetime


def generate_feasible_solutions(algorithm=None, max_solutions=math.inf, max_run_time=math.inf, log_to_console=True):
    # Read variables
    W, H, N, w_i, v_i, S = algorithm.warehouse.W, algorithm.warehouse.H, algorithm.N, algorithm.warehouse.w_i, algorithm.warehouse.v_i, algorithm.warehouse.storage_capacities

    # Start run time
    start_run_time = datetime.now()

    # Return variable
    feasible_solutions = []

    # Maximum aisles
    max_n = round(W / w_i)

    # Order options
    if N <= 5:
        all_order_options = list(itertools.permutations(range(N)))
    else:
        all_order_options = [np.random.sample(N).round(2) for x in range(50)]

    # log
    if log_to_console:
        print("Storage sizes:", S)
        print("Maximum aisles:", max_n)
        print("Order options:", len(all_order_options))

    # Aisle options
    divisible_by = []

    # Find a max_n such that we can easily divide it
    while len(divisible_by) < 2:
        divisible_by = []
        max_n = max_n - 1
        for x in range(2, max_n):
            if max_n % x == 0:
                divisible_by.append(x)

    # Aisle options
    aisle_options = max_n / np.array(divisible_by)
    if len(aisle_options) > 5:
        aisle_options = sample(list(aisle_options), 5)

    # Reduced maximum
    if log_to_console:
        print("Maximum aisles:", max_n)
        print("Aisle options:", aisle_options)

    # All aisle options
    if len(aisle_options) ** N < 1000000:
        all_aisle_options = list(itertools.product(*[aisle_options for x in range(N)]))
    else:
        all_aisle_options = list([sample(list(aisle_options), 1)[0] for x in range(N)] for y in range(100000))

    if len(all_aisle_options) > 0:
        chromosomes = []
        print("Found", str(len(all_order_options) * len(all_aisle_options)), "possible options")
        sampled_aisle_options = sample(all_aisle_options, min(2000, len(all_aisle_options)))
        for order in all_order_options:
            order = np.array(order) / max(order)

            # Choose aisles
            for aisle_option in sampled_aisle_options:
                # Add chromosomes
                chromosomes.append([*order, *aisle_option, *[2 for x in range(N)]])

        # Get warehouse
        warehouse = algorithm.warehouse

        # Shuffle chromosomes
        shuffle(chromosomes)

        if log_to_console:
            print("Processing", len(chromosomes), "possible chromosomes")

        print("Generating feasible solutions")
        for i in tqdm(range(len(chromosomes))):
            # Get chromosome
            chromosome = chromosomes[i]

            # Process chromosome
            obj_value, feasibility = warehouse.process(chromosome)

            # Draw
            if warehouse.feasible:
                feasible_solutions.append((chromosome, obj_value, feasibility))

                # Stop if we have reached acquired amount of solutions
                if len(feasible_solutions) > max_solutions:
                    if log_to_console:
                        print("Generating solutions aborted since we found enough feasible solutions")
                        print("Found " + str(len(feasible_solutions)) + " feasible solutions")
                    return feasible_solutions

            # Stop if we reached the maximum run time
            run_time = datetime.now() - start_run_time
            if run_time.total_seconds() > max_run_time:
                if log_to_console:
                    print("Generating solutions aborted since maximum run time was reached")
                    print("Found " + str(len(feasible_solutions)) + " feasible solutions")
                return feasible_solutions

    return feasible_solutions


# # Get all instances available
# instances = get_instances()
# for instance in instances:
#     # Read variables from instance
#     W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(instance)
#
#     # Genetic algorithm
#     algorithm = GeneticAlgorithm()
#     algorithm.instantiate(instance)
#     warehouse = algorithm.warehouse
#
#     print("\r\nInstance", instance)
#     feasible_solutions = generate_feasible_solutions(algorithm=algorithm, max_solutions=10)
#
#     # Draw a solution
#     if len(feasible_solutions) > 0:
#         print("Found a feasible solution")
#         warehouse.process(chromosome=feasible_solutions[0])
#         warehouse.draw()
#     else:
#         print("No feasible solutions found")
