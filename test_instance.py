from classes import GeneticAlgorithm
from functions.draw_evolution import draw_evolution


# Test specific instance
instance = 21

# Instantiate genetic algorithm
algorithm = GeneticAlgorithm(save_generations=True, iterations=1000)

# Run instance
print("\r\n\r\nRunning instance", instance)
algorithm.run(instance, log_to_console=True, allow_infeasible_parents=True)

# Run
draw_evolution(instances=[instance])
