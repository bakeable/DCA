import math

import numpy as np


class GeneticAlgorithm:
    def __init__(self, N, n_max, k_max, population_size=10):
        # Instantiate variables
        self.N = N
        self.n_max = n_max
        self.k_max = k_max
        self.population = []
        self.population_size = population_size

    def create_random_chromosome(self, N=None, n_max=None, k_max=None):
        # Set variables
        self.N = self.N if N is None else N
        self.n_max = self.n_max if n_max is None else n_max
        self.k_max = self.k_max if k_max is None else k_max

        # Create random order
        order = np.arange(1, self.N + 1)
        np.random.shuffle(order)

        # Create random number of aisles
        aisles = np.random.randint(1, self.n_max, size=self.N)

        # Create random number of cross-aisles
        cross_aisles = np.random.randint(2, self.k_max, size=self.N)

        # Return chromosome
        return [*order, *aisles, *cross_aisles]

    def create_random_chromosomes(self, size):
        # Create random chromosomes
        chromosomes = []
        for i in np.arange(size):
            chromosomes.append(self.create_random_chromosome())

        # Return chromosome
        return chromosomes

    def create_initial_population(self, size=None, feasible=None, process=None):
        # Set population size
        self.population_size = self.population_size if size is None else size

        # Create random chromosomes
        index = 0
        while len(self.population) < self.population_size:
            # Create random chromosome
            chromosome = self.create_random_chromosome()

            # Create item
            item = (index, chromosome, None, None)

            # Already process if available
            if process is not None:
                obj_value, feasibility = process(chromosome)
                item = (index, chromosome, obj_value, feasibility)

            # Add only feasible solutions
            if feasible and item[3] == True or feasible != True:
                # Add to population
                self.population.append(item)

                # Increment index
                index = index + 1

    def create_next_population(self, fittest_size=3, children_size=4):
        # Select fittest chromosomes
        fittest = self.select_fittest(fittest_size)
        fittest_chromosomes = list(map(self.get_chromosomes, fittest))

        # Create children from fittest chromosomes
        if len(fittest) > 0:
            child_chromosomes = self.create_children(fittest_chromosomes, children_size)
        else:
            child_chromosomes = []

        # Create random chromosomes
        random_size = self.population_size - fittest_size - children_size
        random_chromosomes = self.create_random_chromosomes(random_size)

        # Create new population
        self.population = []
        index = 0
        for old_index, chromosome, obj_value, feasibility in fittest:
            if not self.population_contains(chromosome):
                # Append to population
                self.population.append((index, chromosome, obj_value, feasibility))

                # Increment index
                index = index + 1

        # Add new chromosomes to population
        for chromosome in [*child_chromosomes, *random_chromosomes]:
            if not self.population_contains(chromosome):
                # Append to population
                self.population.append((index, chromosome, None, None))

                # Increment index
                index = index + 1

        # Fill population with random chromosomes
        while len(self.population) < self.population_size:
            # Create random chromosome
            chromosome = self.create_random_chromosome()

            if not self.population_contains(chromosome):
                # Append to population
                self.population.append((index, chromosome, None, None))

                # Increment index
                index = index + 1


        # Return new population
        return self.population

    def population_contains(self, chromosome):
        # Stringify each chromosome
        str_chromosomes = list(map(self.get_chromosomes_as_string, self.population))

        # Stringify chromosome
        str_chromosome = "-".join(str(x) for x in chromosome)

        # Return
        return str_chromosome in str_chromosomes

    def get_feasible_solutions(self):
        # Filter population by feasible solutions
        return list(filter(lambda x: x[3] == True, self.population))

    def contains_feasible_solution(self):
        # If len > 0, it contains at least one feasible solution
        return len(self.get_feasible_solutions()) > 0

    def assess_population(self, process):
        for index, chromosome, obj_value, feasibility in self.population:
            if obj_value is None and feasibility is None:
                # Get values
                obj_value, feasibility = process(chromosome)

                # Set values
                self.update(index, chromosome, obj_value, feasibility)

    def select_fittest(self, size):
        # Filter population
        filtered_population = filter(lambda x: x[3] == True, self.population)

        # Sort population
        sorted_population = sorted(filtered_population, key=lambda tup: tup[2])

        # Return fittest
        return sorted_population[:min(size, len(sorted_population))]

    def create_children(self, chromosomes, size):
        children = []
        for i in np.arange(size):
            # Get division from either
            r = np.random.randint(0, len(chromosomes), size=2 * self.N + 2)

            # First random number decides which order we inherit
            order = chromosomes[r[0]][:self.N]

            # 2 to N+1 decide which number of aisles we inherit from which chromosome
            aisles = []
            for j in np.arange(1, self.N+1):
                aisles.append(chromosomes[r[j]][self.N+j-1])

            # N+2 to 2N+1 decide number of cross-aisles we inherit
            cross_aisles = []
            for j in np.arange(self.N+1, 2*self.N+1):
                cross_aisles.append(chromosomes[r[j]][self.N+j-1])

            # Mutate
            aisles_mutation = np.random.randint(-2, 2, size=self.N)
            aisles = np.array(aisles)
            aisles = aisles + aisles_mutation
            aisles[aisles < 1] = 1
            aisles[aisles > 30] = 30

            cross_aisles_mutation = np.random.randint(-2, 2, size=self.N)
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
        return tup[1]

    def get_chromosomes_as_string(self, tup):
        return "-".join(str(x) for x in tup[1])

    def get_chromosome(self, index):
        # Get chromosome from population
        chromosome = self.population[index][0]

        # Return chromosome
        return chromosome

    def update(self, index, chromosome, obj_value, feasibility):
        # Set
        self.population[index] = (index, chromosome, obj_value, feasibility)

        # Return updated
        return self.population[index]