from classes import GeneticAlgorithm
from functions import create_instances
from pathlib import Path
from random import shuffle

# Create some random instances
# create_instances(20)

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
population_sizes = [10, 20, 50, 100]
fittest_sizes = [.1, .2, .3]
children_sizes = [.2, .5, .8]
iterations_sizes = [10, 20, 30, 50, 100]

for instance in range(450):
    # Instantiate genetic algorithm
    algorithm = GeneticAlgorithm(save_generations=False, population_size=100,
                                 fittest_size=.3, children_size=.3, iterations=100, log_to_console=True)

    # Run instance
    print("\r\n\r\nRunning instance", instance)
    algorithm.run(instance+1)

