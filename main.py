import numpy as np
from functions import read_instance
from classes import Warehouse, GeneticAlgorithm

# Read variables from instance
W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance("data/inst1.csv")

# Instantiate warehouse
warehouse = Warehouse(W, H, S, mean_u, alpha, animate=False)

# Instantiate genetic algorithm
algorithm = GeneticAlgorithm(N, warehouse.n_max, warehouse.k_max)

# Start with all feasible solutions
algorithm.create_initial_population(10, feasible=True, process=warehouse.process)
print(algorithm.population)

# Iterate
for i in np.arange(20):
    algorithm.create_next_population()
    algorithm.assess_population(warehouse.process)

# Draw the final best solution
warehouse.animate = True
warehouse.process(algorithm.select_fittest(1)[0][1])
warehouse.draw()

# Return results
if warehouse.feasible:
    print("Final solution is feasible and has a distance of", warehouse.total_travel_distance)
else:
    print("Final solution is infeasible")
