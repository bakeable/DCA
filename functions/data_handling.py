import pandas as pd
import pathlib

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
