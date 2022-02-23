import pandas as pd
import pathlib
import csv
import numpy as np
import math
from random import randrange, random

# Directory path
directory = str(pathlib.Path().resolve())

# Try loading the processed CSV file, otherwise use the standard lookup XLSX
try:
    df = pd.read_csv(directory + "/data/processed_lookup.csv", index_col=[0, 1, 2])
except Exception:
    # Import Excel file
    data = pd.read_excel(directory + "/data/lookup.xlsx", header=1, index_col=[0, 1])

    # Create lookup table
    df = pd.DataFrame(columns=["n", "k", "m", "distance"])
    for index, row in data.iterrows():
        # Convert to lookup table
        m = 1
        for distance in row:
            df = df.append({"n": index[0], "k": index[1], "m": m, "distance": distance}, ignore_index=True)
            m = m + 1

    # Set index
    df = df.set_index(["n", "k", "m"])

    # Save to csv
    df.to_csv(directory + "/data/processed_lookup.csv")


def lookup_travel_distance(n, k, m):
    # Failsafe
    if n < 1 or n > 30 or k < 2 or k > 10:
        return math.inf

    if isinstance(m, list):
        # Calculate average travel distance based on distribution of order sizes
        order_sizes = np.arange(1, len(m) + 1)
        m = np.array(m)

        # Calculate expected travel distance
        expected_travel_distance = 0
        i = 0
        for size in order_sizes[m > 0]:
            expected_travel_distance = expected_travel_distance + m[m > 0][i] * df.loc[(n, k, size)]["distance"]
            i = i + 1

        # Return expected travel distance
        return expected_travel_distance
    else:
        return df.loc[(n, k, m)]["distance"]


def create_instances(number, max_N=10):
    for index in range(number):
        # Number of picking areas
        N = randrange(4, max_N)

        # Aisle sizes
        w_i = randrange(1, 10)
        v_i = randrange(1, 10)

        # Storage capacities
        S = np.random.randint(100, 1000, size=N)

        # Replenishment
        alpha = [5 * random() for x in range(N)]

        # Order size distributions
        u = []
        for i in np.arange(N):
            array = np.random.randint(100, size=30)
            dist = array / sum(array)
            u.append(dist)

        # Calculate mean order size per picking area
        mean_u = []
        for dist in u:
            number_items = np.arange(1, len(dist) + 1)
            mean_u.append(round(np.inner(dist, number_items)))

        # Surface
        surface = 0
        for s_i in S:
            # Random number of aisles
            n = randrange(1, 5 * N)

            # Calculate width and height
            w = w_i * n
            h = s_i / n + v_i * 2

            # Add to surface
            surface = surface + w * h

        # Add a random percentage to required surface
        surface = (1 + random()) * surface

        # Width and height
        W = randrange(round(math.sqrt(surface) / 3), round(3 * math.sqrt(surface)))
        H = math.ceil(surface / W)

        # Write lines
        f = open('input/inst' + str(3 + index) + '.csv', 'w')

        # Write W
        f.write(str(W) + "\n")

        # Write H
        f.write(str(H) + "\n")

        # Write N
        f.write(str(N) + "\n")

        # Write w_i
        f.write(str(w_i) + "\n")

        # Write v_i
        f.write(str(v_i) + "\n")

        # Write S
        f.write(",".join(str(s_i) for s_i in S) + "\n")

        # Write alpha
        f.write(",".join(str(a) for a in alpha) + "\n")

        # Write distributio
        for u_i in u:
            f.write(",".join(str(x) for x in u_i) + "\n")

        # Close CSV file
        f.close()


def read_instance(instance):
    # Import csv
    path = directory + "/input/inst" + str(instance) + ".csv"
    with open(path, newline='') as f:
        reader = csv.reader(f)

        # Width and height
        W = int(next(reader)[0])
        H = int(next(reader)[0])

        # Number of picking areas
        N = int(next(reader)[0])

        # Aisle sizes
        w_i = int(next(reader)[0])
        v_i = int(next(reader)[0])

        # Storage capacities
        S = [int(x) for x in next(reader)]

        # Replenishment
        alpha = [float(x) for x in next(reader)]

        # Order size distributions
        u = []
        for i in np.arange(N):
            u.append([float(x) for x in next(reader)])

    # Calculate mean order size per picking area
    mean_u = []
    for dist in u:
        number_items = np.arange(1, len(dist) + 1)
        mean_u.append(round(np.inner(dist, number_items)))

    # Return
    return W, H, N, w_i, v_i, S, alpha, u, mean_u


def write_instance(instance, obj_value, coordinates):
    # Write lines
    f = open('output/sol' + str(instance) + '.csv', 'w')

    # Write group number
    f.write("A4\n")

    # Write instance number
    f.write(str(instance) + "\n")

    # Write objective value
    f.write(str(round(obj_value, 2)) + "\n")

    # Write coordinates
    for coordinate in coordinates:
        x, y, n, k = coordinate
        f.write(str('%.2f' % x) + "," + str('%.2f' % y) + "," + str(int(n)) + "," + str(int(k)) + "\n")

    # Close CSV file
    f.close()
