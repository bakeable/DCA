import pandas as pd
import pathlib
import csv
import numpy as np
import os
import math
from random import randrange, random

# Directory path
directory = str(pathlib.Path().resolve())

# Try loading the processed CSV file, otherwise use the standard lookup XLSX
try:
    df_g = pd.read_csv(directory + "/data/processed_lookup_g.csv", index_col=[0, 1, 2])
    df_h = pd.read_csv(directory + "/data/processed_lookup_h.csv", index_col=[0, 1, 2])
    df_f = pd.read_csv(directory + "/data/processed_lookup_f.csv", index_col=[0, 1, 2])
except Exception as e:
    print(str(e))
    for sheet in ["g","h","f"]:
        print(sheet)
        # Import Excel file
        data = pd.read_excel(directory + "/data/lookup.xlsx", sheet, header=1, index_col=[0, 1])

        # Create lookup table
        df = pd.DataFrame(columns=["n", "k", "m", "distance"])
        for index, row in data.iterrows():
            # Convert to lookup table
            m = 1
            for distance in row:
                df = df.append({"n":int(index[0]), "k": int(index[1]), "m": int(m), "distance": distance}, ignore_index=True)
                m = m + 1

        # Set index
        df = df.set_index(["n", "k", "m"])

        # Save to csv
        df.to_csv(directory + "/data/processed_lookup_" + sheet + ".csv")

    df_g = pd.read_csv(directory + "/data/processed_lookup_g.csv", index_col=[0, 1, 2])
    df_h = pd.read_csv(directory + "/data/processed_lookup_h.csv", index_col=[0, 1, 2])
    df_f = pd.read_csv(directory + "/data/processed_lookup_f.csv", index_col=[0, 1, 2])


def lookup_travel_distance(n, k, m, S=1, w=.2, v=.1):
    # Failsafes
    if n < 1 or n > 30 or k < 2 or k > 10:
        return math.inf

    if isinstance(m, list):
        # Calculate average travel distance based on distribution of order sizes
        order_sizes = np.arange(1, len(m) + 1)
        m = np.array(m)


        # Calculate expected travel distance
        expected_travel_distance = 0
        i = 0
        for size in order_sizes:
            g = df_g.loc[(n, k, size)]["distance"]
            h = df_h.loc[(n, k, size)]["distance"]
            f = df_f.loc[(n, k, size)]["distance"]
            T_im = S * (g / n) + w * h + v * f
            expected_travel_distance = expected_travel_distance + m[i] * T_im
            i = i + 1

        # Return expected travel distance
        return round(expected_travel_distance, 2)
    else:
        g = df_g.loc[(n, k, m)]["distance"]
        h = df_h.loc[(n, k, m)]["distance"]
        f = df_f.loc[(n, k, m)]["distance"]
        T_i1 = S * (g / n) + w * h + v * f
        return round(T_i1, 2)


def create_instances(number, max_N=20):
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


def write_instance(instance, obj_value, coordinates, force=True):
    if math.isinf(obj_value) or obj_value == 0:
        obj_value = -1

    # Check if existing solution is better
    try:
        path = directory + "/output/sol" + str(instance) + ".csv"
        with open(path, newline='') as f:
            reader = csv.reader(f)

            # Read lines
            group_number = next(reader)[0]
            old_instance = next(reader)[0]
            old_obj_value = float(next(reader)[0])
            print(group_number, old_instance, old_obj_value, "=>", obj_value)
    except:
        print("Writing new solution to instance" + str(instance))
        old_obj_value = -1

    if old_obj_value > obj_value or old_obj_value == -1 or force:
        # Write lines
        f = open('output/sol' + str(instance) + '.csv', 'w')

        # Write group number
        f.write("A4\n")

        # Write instance number
        f.write(str(instance) + "\n")

        # Write objective value
        f.write(str(round(obj_value, 2)) + "\n")

        # Write coordinates if objective value is greater than or equal to zero
        if obj_value >= 0:
            for coordinate in coordinates:
                f.write(",".join(str(x) for x in coordinate) + "\n")

        # Close CSV file
        f.close()
        print("Written solution")
    else:
        print("A better solution to instance " + str(instance) + " already exists")


def get_instances():
    # Get all instances
    instances = []
    directory = str(pathlib.Path().resolve())
    pathlist = pathlib.Path(directory + "/input").glob("*.csv")
    for path in pathlist:
        # Convert to string
        path_in_str = str(path)

        # Get instance
        instances.append(int(path_in_str.split("inst").pop().split(".csv").pop(0)))

    # Sort instances
    return sorted(instances)

def get_solutions():
    # Get all solutions
    solutions = []
    directory = str(pathlib.Path().resolve())
    pathlist = pathlib.Path(directory + "/output").glob("*.csv")
    for path in pathlist:
        # Convert to string
        path_in_str = str(path)

        # Get instance
        solutions.append(int(path_in_str.split("sol").pop().split(".csv").pop(0)))

    # Sort instances
    return sorted(solutions)


def create_null_solutions():
    for i in range(1, 451):
        write_instance(i, -1, [])

def import_solutions():
    # Get all solutions
    directory = str(pathlib.Path().resolve())
    pathlist = pathlib.Path(directory + "/output").glob("*.csv")
    for path in pathlist:
        # Convert to string
        path_in_str = str(path)

        # Get instance
        instance = int(path_in_str.split("sol").pop().split(".csv").pop(0))

        if import_solution(instance):
            # Import csv
            from_path = directory + "/download/output/sol" + str(instance) + ".csv"
            to_path = path
            os.replace(from_path, to_path)
            print(from_path, to_path)


    # Sort instances

def get_unsolved_instances():
    # Get all solutions
    unsolved = []
    directory = str(pathlib.Path().resolve())
    pathlist = pathlib.Path(directory + "/output").glob("*.csv")
    for path in pathlist:
        # Convert to string
        path_in_str = str(path)

        # Get instance
        instance = int(path_in_str.split("sol").pop().split(".csv").pop(0))

        if read_obj_value(instance) < 0:
            unsolved.append(instance)

    # Sort instances
    return sorted(unsolved)

def read_obj_value(instance):
    # Import csv
    path = directory + "/output/sol" + str(instance) + ".csv"
    with open(path, newline='') as f:
        reader = csv.reader(f)

        group = next(reader)[0]
        i = int(next(reader)[0])
        obj_value = float(next(reader)[0])

    # Return
    return obj_value


def import_solution(instance):
    # Current csv
    path = directory + "/output/sol" + str(instance) + ".csv"
    with open(path, newline='') as f:
        reader = csv.reader(f)

        group = next(reader)[0]
        i = int(next(reader)[0])
        obj_value_1 = float(next(reader)[0])

    # Import csv
    path = directory + "/download/output/sol" + str(instance) + ".csv"
    with open(path, newline='') as f:
        reader = csv.reader(f)

        group = next(reader)[0]
        i = int(next(reader)[0])
        obj_value_2 = float(next(reader)[0])

    # Return true if we need to import value
    print("new value", obj_value_2, "old value", obj_value_1, obj_value_2 < obj_value_1 and obj_value_2 != -1 or obj_value_1 == -1 and obj_value_2 != -1)
    return obj_value_2 < obj_value_1 and obj_value_2 != -1 or obj_value_1 == -1 and obj_value_2 != -1

