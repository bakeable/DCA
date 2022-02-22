import math
from random import random
import numpy as np
from classes import Warehouse
from functions import read_instance, write_instance
from tqdm import tqdm


class GeneticAlgorithm:
    def __init__(self, population_size=30, iterations=50, fittest_size=.3, children_size=.3):
        # Instantiate warehouse
        self.warehouse = None

        # Instantiate variables
        self.N = None
        self.n_min, self.k_min, self.n_max, self.k_max = None, None, None, None

        # Instantiate population
        self.population = []
        self.population_size = population_size

        # Set parameters
        self.iterations = iterations
        self.fittest_size = fittest_size
        self.children_size = children_size

        self.fittest_obj_value = math.inf
        self.obj_value_decrease = 0

    def instantiate(self, instance):
        # Read variables from instance
        W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(instance)

        # Instantiate warehouse
        self.warehouse = Warehouse(W, H, S, u, alpha, animate=False, w_i=w_i, v_i=v_i)

        # Instantiate variables
        self.N = N
        self.n_min, self.k_min, self.n_max, self.k_max = self.warehouse.n_min, self.warehouse.k_min, self.warehouse.n_max, self.warehouse.k_max

    def run(self, instance):
        # Instantiate
        self.instantiate(instance)

        # Create initial population
        self.create_initial_population(min_feasible=0)

        # Add one feasible solution
        if instance == 2:
            self.population.append(([2, 4, 1, 3, 5, 4, 2, 4, 2, 4, 2, 2, 2, 2, 2], 851.4766715860002, True))

        # Iterate
        last_improvement = 0
        while last_improvement < 1:
            improved = False
            print("Starting new set of iterations")
            for i in tqdm(range(self.iterations)):
                # Create next population
                self.create_next_population()

                # Set fittest objective value
                fittest = self.select_fittest(1)
                if len(fittest) > 0:
                    if self.fittest_obj_value > fittest[0][1]:
                        self.obj_value_decrease = self.fittest_obj_value - fittest[0][1]
                        self.fittest_obj_value = fittest[0][1]
                        last_improvement = 0
                        improved = True

            if improved:
                print("\r\nObjective value improved")
            else:
                print("\r\nObjective value did not improve")

            # Increment time from last improvement
            last_improvement = last_improvement + 1

        # Get final solution
        solution = self.get_final_solution()

        # If we have a solution, report on it
        if solution is not None:
            # Process solution
            self.warehouse.process(solution[0])

            # Report
            if self.warehouse.feasible:
                print("\r\nA feasible solution was found")
                print("Optimal chromosome:", solution[0])
                print("Total distance:", self.warehouse.total_travel_distance)
                print("PA layout:", self.warehouse.get_PA_dimensions())
            else:
                print("\r\nAlgorithm did not find a feasible solution")

        else:
            # Report
            print("\r\nAlgorithm did not find a feasible solution")

            # Take best infeasible
            solution = self.select_fittest(1, allow_infeasible=True)[0]

            # Process solution
            self.warehouse.process(solution[0])

        # Draw solution
        self.warehouse.draw(save=True, filename=f'output/sol{instance}.png')

        # Write output
        write_instance(instance, self.warehouse.total_travel_distance if self.warehouse.feasible else math.inf, self.warehouse.get_PA_dimensions())

    def create_random_chromosome(self):
        # Create random order
        order = np.arange(1, self.N + 1)
        np.random.shuffle(order)

        # Create random number of aisles
        aisles = np.random.randint(1, self.n_max, size=self.N)

        # There must be a minimum number of aisles to fit in the height
        aisles[aisles < self.n_min] = self.n_min[aisles < self.n_min]

        # Create random number of cross-aisles
        cross_aisles = np.random.randint(self.k_min, self.k_max, size=self.N)

        # Return chromosome
        return [*order, *aisles, *cross_aisles]

    def create_random_chromosomes(self, size):
        # Create random chromosomes
        chromosomes = []
        for i in np.arange(size):
            chromosomes.append(self.create_random_chromosome())

        # Return chromosome
        return chromosomes

    def create_initial_population(self, min_feasible=0):
        # Create random chromosomes
        feasible = 0
        while len(self.population) < self.population_size:
            # Create random chromosome
            chromosome = self.create_random_chromosome()

            # Process chromosome
            obj_value, feasibility = self.warehouse.process(chromosome)

            # Set item
            item = (chromosome, obj_value, feasibility)

            # Add only feasible solutions
            if feasible < min_feasible and item[2] is True or feasible >= min_feasible:
                # Add to population
                self.population.append(item)

                # Number of feasible items
                if item[2]:
                    feasible = feasible + 1

    def create_next_population(self, fittest_size=None, children_size=None):
        # Set fittest size
        self.fittest_size = fittest_size if fittest_size is not None else self.fittest_size
        self.children_size = children_size if children_size is not None else self.children_size

        # Select fittest chromosomes
        fittest = self.select_fittest(int(self.fittest_size * self.population_size))
        fittest_chromosomes = list(map(self.get_chromosomes, fittest))

        # Create children from fittest chromosomes
        if len(fittest) > 0:
            child_chromosomes = self.create_children(fittest_chromosomes, int(self.children_size * self.population_size))
        else:
            child_chromosomes = []

        # Create random chromosomes
        random_size = 1 - self.fittest_size - self.children_size
        random_chromosomes = self.create_random_chromosomes(int(random_size * self.population_size))

        # Create new population
        self.population = []
        for chromosome, obj_value, feasibility in fittest:
            if not self.population_contains(chromosome):
                # Append to population
                self.add_to_population(chromosome, obj_value=obj_value, feasibility=feasibility, process=False)

        # Add new chromosomes to population
        for chromosome in [*child_chromosomes, *random_chromosomes]:
            if not self.population_contains(chromosome):
                # Append to population
                self.add_to_population(chromosome, process=True)

        # Fill population with random chromosomes
        while len(self.population) < self.population_size:
            # Create random chromosome
            chromosome = self.create_random_chromosome()

            if not self.population_contains(chromosome):
                # Append to population
                self.add_to_population(chromosome, process=True)

        # Return new population
        return self.population

    def add_to_population(self, chromosome, obj_value=None, feasibility=None, process=False):
        # Process the item if required
        if process is True:
            # Process chromosome
            obj_value, feasibility = self.warehouse.process(chromosome)

            # Set item
            item = (chromosome, obj_value, feasibility)
        else:
            # Set item
            item = (chromosome, obj_value, feasibility)

        # Add item
        self.population.append(item)

    def population_contains(self, chromosome):
        # Stringify each chromosome
        str_chromosomes = list(map(self.get_chromosomes_as_string, self.population))

        # Stringify chromosome
        str_chromosome = "-".join(str(x) for x in chromosome)

        # Return
        return str_chromosome in str_chromosomes

    def get_feasible_solutions(self):
        # Filter population by feasible solutions
        return list(filter(lambda x: x[2] == True, self.population))

    def contains_feasible_solution(self):
        # If len > 0, it contains at least one feasible solution
        return len(self.get_feasible_solutions()) > 0

    def assess_population(self, process):
        index = 0
        for chromosome, obj_value, feasibility in self.population:
            if obj_value is None and feasibility is None:
                # Get values
                obj_value, feasibility = process(chromosome)

                # Set values
                self.update(index, chromosome, obj_value, feasibility)

                # Increment index
                index = index + 1

    def select_fittest(self, size, allow_infeasible=False):
        # Filter population
        filtered_population = self.population if allow_infeasible else filter(lambda x: x[2] == True, self.population)

        # Sort population
        sorted_population = sorted(filtered_population, key=lambda tup: tup[1])

        # Return fittest
        return sorted_population[:min(size, len(sorted_population))]

    def create_children(self, chromosomes, size):
        children = []
        for i in np.arange(size):
            # Get division from either
            r = np.random.randint(0, len(chromosomes), size=2 * self.N + 2)

            # First random number decides which order we inherit
            order = chromosomes[r[0]][:self.N]
            if random() > .5:
                np.random.shuffle(order)

            # 2 to N+1 decide which number of aisles we inherit from which chromosome
            aisles = []
            for j in np.arange(1, self.N + 1):
                aisles.append(chromosomes[r[j]][self.N + j - 1])

            # N+2 to 2N+1 decide number of cross-aisles we inherit
            cross_aisles = []
            for j in np.arange(self.N + 1, 2 * self.N + 1):
                cross_aisles.append(chromosomes[r[j]][self.N + j - 1])

            # Mutate
            aisles_mutation = np.random.randint(-1, 1, size=self.N)
            aisles = np.array(aisles)
            aisles = aisles + aisles_mutation
            aisles[aisles < 1] = 1
            aisles[aisles > 30] = 30

            cross_aisles_mutation = np.random.randint(-1, 1, size=self.N)
            cross_aisles = np.array(cross_aisles)
            cross_aisles = cross_aisles + cross_aisles_mutation
            cross_aisles[cross_aisles < 2] = 2
            cross_aisles[cross_aisles > 10] = 10

            # Create child
            child = [*order, *aisles, *cross_aisles]

            # Append child
            children.append(child)

        return children

    def get_chromosomes(self, tup):
        return tup[0]

    def get_chromosomes_as_string(self, tup):
        return "-".join(str(x) for x in tup[0])

    def get_chromosome(self, index):
        # Get chromosome from population
        chromosome = self.population[index][0]

        # Return chromosome
        return chromosome

    def update(self, index, chromosome, obj_value, feasibility):
        # Set
        self.population[index] = (chromosome, obj_value, feasibility)

        # Return updated
        return self.population[index]

    def get_fittest_chromosome(self):
        return self.select_fittest(1)[0][0]


    def get_final_solution(self):
        fittest = self.select_fittest(1)
        if len(fittest) == 0:
            return None
        else:
            return fittest[0]
