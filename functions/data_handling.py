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
    return df.loc[(n, k, m)]["distance"]


def read_instance(filename):
    # Import csv
    path = directory + "/" + filename
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

