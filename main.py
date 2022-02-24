from classes import GeneticAlgorithm
from functions import create_instances
from pathlib import Path

# reate some random instances
create_instances(20)

# Get all instances
instances = []
directory = str(Path().resolve())
pathlist = Path(directory + "/input").glob("*.csv")
for path in pathlist:
    # Convert to string
    path_in_str = str(path)

    # Get instance
    instances.append(int(path_in_str.split("inst").pop().split(".csv").pop(0)))

# Sort instances
instances = sorted(instances)

# Run all instances
for instance in instances:
    # Instantiate genetic algorithm
    algorithm = GeneticAlgorithm(save_generations=True)

    # Run instance
    print("\r\n\r\nRunning instance", instance)
    algorithm.run(instance, log_to_console=True)

