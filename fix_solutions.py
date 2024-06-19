import math

from functions import read_instance, lookup_travel_distance, write_instance
import pathlib
import csv
import pandas as pd

# Directory path
directory = str(pathlib.Path().resolve())

def fix_solution(instance):
    # Instance
    W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(instance)

    # Current csv
    path = directory + "/output/sol" + str(instance) + ".csv"
    with open(path, newline='') as f:
        reader = csv.reader(f)

        group = next(reader)[0]
        i = int(next(reader)[0])
        obj_value = float(next(reader)[0])

        total_distance = 0
        i = 0
        coordinates = []
        for row in reader:
            x,y,n,k = row
            x = int(x)
            y = float(y)
            n = int(n)
            k = int(k)

            travel_distance = round(2 * y * (1 + alpha[i]),2) + round(alpha[i],2) * lookup_travel_distance(n, k, 1, S[i], w_i, v_i) + lookup_travel_distance(n, k, u[i], S[i], w_i, v_i)
            total_distance = total_distance + round(travel_distance,2)
            coordinates.append([x,y,n,k])
            i = i + 1

    print(total_distance)
    if total_distance is math.inf or total_distance == 0:
        write_instance(instance, -1, [], force=True)
    else:
        write_instance(instance, round(total_distance, 2), coordinates, force=True)


for i in range(1,450):
    fix_solution(i)