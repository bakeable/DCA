from classes import Warehouse
from functions import read_instance

# Read variables from instance
W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(2)

# Instantiate warehouse
warehouse = Warehouse(W, H, S, u, alpha, animate=True, w_i=w_i, v_i=v_i)

# Test chromosome
warehouse.process([0.32, 0.57, 0.42, 0.3, 0.9, 2.0, 2.0, 2.0, 2.0, 4.0, 2, 2, 2, 2, 4])
print(warehouse.total_travel_distance)
warehouse.draw()