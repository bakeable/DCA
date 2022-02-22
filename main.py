import numpy as np
from functions import read_instance, write_instance
from classes import Warehouse, GeneticAlgorithm
import math



# Instantiate genetic algorithm
algorithm = GeneticAlgorithm()
algorithm.run(2)