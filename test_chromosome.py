from classes import Warehouse
from functions import read_instance

# Read variables from instance
W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(2)

# Instantiate warehouse
warehouse = Warehouse(W, H, S, u, alpha, animate=True, w_i=w_i, v_i=v_i)

# Test chromosome
warehouse.process([0.4, 0.1, 0.2, 0.6, 0, 4, 2, 4, 2, 4, 2, 2, 2, 2, 2])
warehouse.draw()