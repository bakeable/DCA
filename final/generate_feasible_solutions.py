import numpy as np
import math
from random import sample
from datetime import datetime


def generate_feasible_solutions(algorithm=None, max_solutions=math.inf, max_run_time=math.inf, log_to_console=True, iteration=0):
    # Read variables
    W, H, N, w_i, v_i, S = algorithm.warehouse.W, algorithm.warehouse.H, algorithm.N, algorithm.warehouse.w_i, algorithm.warehouse.v_i, algorithm.warehouse.storage_capacities

    # Start run time
    start_run_time = datetime.now()

    # Return variable
    feasible_solutions = []

    # Maximum aisles
    max_n = round((W / w_i) - 0.5)

    # Aisle options
    aisle_options = []

    # Find aisle options
    tmp_n = max_n
    while len(aisle_options) < 6 + iteration:
        tmp_n = tmp_n - 1
        for x in range(2, tmp_n):
            option = tmp_n / x
            if tmp_n % x == 0 and option not in aisle_options:
                aisle_options.append(option)

    # Aisle options
    if len(aisle_options) > 5:
        aisle_options = sample(list(aisle_options), 5)

    # Reduced maximum
    if log_to_console:
        print("Storage sizes:", S)
        print("Maximum aisles:", max_n)
        print("Aisle options:", aisle_options)

    if len(aisle_options) > 0:
        chromosomes = []
        for i in range(10000):
            chromosomes.append([*np.random.sample(N).round(2), *[sample(list(aisle_options), 1)[0] for x in range(N)], *[2 for x in range(N)]])

        # Get warehouse
        warehouse = algorithm.warehouse

        if log_to_console:
            print("Processing", len(chromosomes), "possible chromosomes")

        print("Generating feasible solutions")
        for i in range(len(chromosomes)):
            # Get chromosome
            chromosome = chromosomes[i]

            # Process chromosome
            obj_value, feasibility = warehouse.process(chromosome)

            # Draw
            if warehouse.feasible:
                print("Found a feasible chromosome\r\n", chromosome, "\r\nwith objective value", obj_value)
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


