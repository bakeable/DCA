from classes import GeneticAlgorithm
from functions import get_unsolved_instances, import_solutions
# from pathlib import Path
from random import sample
import os

# # Create some random instances
# # create_instances(20)
#
# # Get all instances
# instances = []
# directory = str(Path().resolve())
# pathlist = Path(directory + "/input").glob("*.csv")
# for path in pathlist:
#     # Convert to string
#     path_in_str = str(path)
#
#     # Get instance
#     instances.append(int(path_in_str.split("inst").pop().split(".csv").pop(0)))
#
# # Sort instances
# instances = sorted(instances)


# Run all unsolved instances
no_solution = get_unsolved_instances()
print(len(no_solution))

for instance in sample(no_solution, 1):
    # Instance
    if not os.path.exists("./data/diagnostics/instance" + str(instance)):
        os.makedirs("./data/diagnostics/instance" + str(instance))

    # Instantiate genetic algorithm
    algorithm = GeneticAlgorithm(save_generations=False, population_size=20, penalty=100000,
                                 fittest_size=.1, random_size=.1, children_size=.8, iterations=100, initial_random_factor=0, log_to_console=True)

    # Run instance
    print("\r\n\r\nRunning instance", instance)
    algorithm.run(instance)

