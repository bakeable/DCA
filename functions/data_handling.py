import pandas as pd
import pathlib
import csv
import numpy as np

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
    if isinstance(m, list):
        # Calculate average travel distance based on distribution of order sizes
        order_sizes = np.arange(1, len(m)+1)
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
        number_items = np.arange(1, len(dist)+1)
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
        f.write(",".join(str(x) for x in coordinate) + "\n")

    # Close CSV file
    f.close()


