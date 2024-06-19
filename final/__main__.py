from classes import GeneticAlgorithm
import os
import sys

parameters = []
if __name__ == "__main__":
    instance = int(sys.argv[1])

    # Instance
    if not os.path.exists("./data/diagnostics/instance" + str(instance)):
        os.makedirs("./data/diagnostics/instance" + str(instance))

    # Instantiate genetic algorithm
    algorithm = GeneticAlgorithm(save_generations=False, population_size=100,
                                 fittest_size=.33, random_size=.33, children_size=.33, penalty=100000, initial_random_factor=5, iterations=100, log_to_console=True)

    # Run instance
    print("\r\n\r\nRunning instance", instance)
    algorithm.run(instance)

