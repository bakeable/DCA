from classes import GeneticAlgorithm
from functions.draw_evolution import draw_evolution


# Test specific instance
instance = 2

# Instantiate genetic algorithm
algorithm = GeneticAlgorithm(save_generations=True)

# Run instance
print("\r\n\r\nRunning instance", instance)
algorithm.run(instance, log_to_console=True)

# Run
draw_evolution(instances=[2])
