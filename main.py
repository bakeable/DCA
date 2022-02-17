import numpy as np
from classes import Warehouse, GeneticAlgorithm
from constants import W, H

# Instantiate warehouse
N = 4
storage_capacities = [400, 500, 500, 400]
order_sizes = [25, 12, 8, 12]
warehouse = Warehouse(W, H, storage_capacities, order_sizes, animate=False)

# Instantiate genetic algorithm
algorithm = GeneticAlgorithm(N, warehouse.n_max, warehouse.k_max)
algorithm.create_initial_population(10)
algorithm.assess_population(warehouse.process)

for i in np.arange(20):
    algorithm.create_next_population()
    algorithm.assess_population(warehouse.process)
    print(algorithm.population)

warehouse.animate = True
warehouse.process([3, 2, 4, 1, 6, 17, 19, 8, 5, 7, 4, 4])

print(warehouse.total_travel_distance, warehouse.feasible)