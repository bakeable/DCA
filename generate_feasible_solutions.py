from classes import Warehouse, PickingArea, GeneticAlgorithm
from functions import read_instance
import itertools
import numpy as np
import math
from random import random, randrange, choice, sample
from copy import copy
from functions.data_handling import get_instances
from tqdm import tqdm


def generate_feasible_solutions(W, H, N, w_i, v_i, S, algorithm=GeneticAlgorithm()):
    # Return variable
    feasible_chromosomes = []

    # Storage sizes
    print("Storage sizes:", S)

    # Maximum aisles
    max_n = round(W / w_i)
    print("Maximum aisles:", max_n)

    # Order options
    if N <= 5:
        all_order_options = list(itertools.permutations(range(N)))
    else:
        all_order_options = [np.random.sample(N).round(2) for x in range(50)]

    print("Order options:", len(all_order_options))

    # Aisle options
    divisible_by = []
    for x in range(2, max_n):
        if max_n % x == 0:
            divisible_by.append(x)

    # Find a max_n such that we can easily divide it
    while len(divisible_by) < 1:
        divisible_by = []
        max_n = max_n - 1
        for x in range(2, max_n):
            if max_n % x == 0:
                divisible_by.append(x)

    aisle_options = max_n / np.array(divisible_by)

    print("Aisle options:", aisle_options)
    # Determine optimal aisle options
    optimal_length = len(aisle_options)
    while optimal_length ** N > 5000:
        optimal_length = optimal_length - 1

    print("Optimal option length:", optimal_length)

    if len(aisle_options) > optimal_length:
        aisle_options = sample(list(aisle_options), k=optimal_length)
        print(aisle_options)

    # Reduce aisle options
    ready = False
    reduced_aisle_options = []
    while not ready:
        all_aisle_options = list(itertools.product(*[aisle_options for x in range(N)]))
        print("All aisle options:", len(all_aisle_options))

        reduced_aisle_options = []
        for aisle_option in all_aisle_options:
            surface = sum(w_i * np.array(aisle_option) * (np.array(S) / np.array(aisle_option) + v_i * 2))
            if surface <= W * H:
                reduced_aisle_options.append((aisle_option, surface))

        print("Reduced aisle options:", len(reduced_aisle_options))
        reduced_aisle_options = sorted(reduced_aisle_options, key=lambda tup: tup[1])

        # Determine when ready
        if len(reduced_aisle_options) < 1000 or len(aisle_options) <= 1:
            ready = True
        else:
            aisle_options = aisle_options[:-1]

    if len(reduced_aisle_options) > 0:
        print("Start calculations")
        chromosomes = []
        for order in all_order_options:
            order = np.array(order) / max(order)

            # Choose aisles
            for aisle_option, surface in reduced_aisle_options:
                # Add chromosomes
                chromosomes.append([*order, *aisle_option, *[2 for x in range(N)]])

        print(len(chromosomes), "possible chromosomes")

        # Get warehouse
        warehouse = algorithm.warehouse

        i = 0
        for i in tqdm(range(len(chromosomes))):
            # Get chromosome
            chromosome = chromosomes[i]

            # Process chromosome
            warehouse.process(chromosome)

            # Draw
            if warehouse.feasible:
                feasible_chromosomes.append(chromosome)

    return feasible_chromosomes


# Get all instances available
instances = get_instances()
for instance in instances:
    # Read variables from instance
    W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(instance)

    # Genetic algorithm
    algorithm = GeneticAlgorithm()
    algorithm.instantiate(instance)
    warehouse = algorithm.warehouse

    print("\r\nInstance", instance)
    feasible_solutions = generate_feasible_solutions(W, H, N, w_i, v_i, S, algorithm=algorithm)

    # Draw a solution
    if len(feasible_solutions) > 0:
        print("Found a feasible solution")
        warehouse.process(chromosome=feasible_solutions[0])
        warehouse.draw()
    else:
        print("No feasible solutions found")
