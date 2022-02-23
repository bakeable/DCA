from classes import GeneticAlgorithm
from functions import create_instances
from pathlib import Path

# Create some random instances
create_instances(20)

# Directory path
directory = str(Path().resolve())
pathlist = Path(directory + "/input").glob("*.csv")
for path in pathlist:
    # Convert to string
    path_in_str = str(path)

    # Get instance
    instance = int(path_in_str.split("inst").pop().split(".csv").pop(0))

    # Instantiate genetic algorithm
    algorithm = GeneticAlgorithm()

    # Run instance
    print("\r\n\r\nRunning instance", instance)
    algorithm.run(instance)

