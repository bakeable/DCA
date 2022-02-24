import math
from random import random, randrange, sample
import numpy as np
from classes import Warehouse
from functions import read_instance, write_instance
from tqdm import tqdm
import pandas as pd


def get_chromosomes(tup):
    return tup[0]


def get_chromosomes_as_string(tup):
    return "-".join(str(x) for x in tup[0])


class GeneticAlgorithm:
    def __init__(self, population_size=30, iterations=10, fittest_size=.2, children_size=.3, save_generations=False):
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

        # Save generations
        self.save_generations = save_generations
        self.generation_number = 0
        self.generations = pd.DataFrame(columns=["generation", "mother", "father", "child"])

    def instantiate(self, instance):
        # Read variables from instance
        W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(instance)

        # Instantiate warehouse
        self.warehouse = Warehouse(W, H, S, u, alpha, animate=False, w_i=w_i, v_i=v_i)

        # Instantiate variables
        self.N = N
        self.n_min, self.k_min, self.n_max, self.k_max = self.warehouse.n_min, self.warehouse.k_min, self.warehouse.n_max, self.warehouse.k_max

    def run(self, instance, log_to_console=False):
        # Instantiate
        self.instantiate(instance)

        # Create initial population
        self.create_initial_population(min_feasible=0)

        # # Add one feasible solution
        # if instance == 2:
        #     self.population.append(([0.4, 0.8, 0.2, 0.6, 0, 4, 2, 4, 2, 4, 2, 2, 2, 2, 2], 851.4766715860002, True))
        #     self.population.append(([0.4, 0.8, 0.2, 0.6, 0, 2, 2, 2, 2, 4, 2, 2, 3, 2, 4], 300, True))

        # Iterate
        last_improvement = 0
        while last_improvement < 1:
            # Increment time from last improvement
            last_improvement = last_improvement + 1

            # Keep track of improvement
            total_improved = 0
            prev_fittest_obj_value = self.fittest_obj_value

            # Log
            if log_to_console:
                print("Starting new set of iterations\r\n")

            for i in tqdm(range(self.iterations)):
                # Create next population
                self.create_next_population()

                # Set fittest objective value
                fittest = self.select_fittest(1)
                if len(fittest) > 0:
                    if self.fittest_obj_value > fittest[0][1]:
                        self.obj_value_decrease = self.fittest_obj_value - fittest[0][1]
                        total_improved = total_improved + self.obj_value_decrease
                        self.fittest_obj_value = fittest[0][1]
                        last_improvement = 0

            # Log
            if log_to_console:
                if last_improvement == 0:
                    if total_improved == math.inf:
                        print("\r\nAt least one feasible solution was found with objective value",
                              self.fittest_obj_value)
                    else:
                        perc_improved = round((total_improved / prev_fittest_obj_value) * 100, 2)
                        print("\r\nObjective value improved by", round(total_improved, 2), "(-", perc_improved,
                              "%), now given by", self.fittest_obj_value)
                else:
                    print("\r\nObjective value did not improve")

        # Get final solution, this returns None if there is no feasible solution
        solution = self.get_final_solution()

        # If we have a solution, report on it
        if solution is not None:

            # Log
            if log_to_console:
                print("\r\nA feasible solution was found")
                print("Optimal chromosome:", solution[0])
                print("Total distance:", solution[1])
                print("PA layout:", self.warehouse.get_PA_dimensions())

        else:
            # Log
            if log_to_console:
                print("\r\nAlgorithm did not find a feasible solution")

            # Take best infeasible
            solution = self.select_fittest(1, allow_infeasible=True)[0]

        # Process solution
        self.warehouse.process(solution[0])

        # Draw solution as a PNG
        filename = f'output/sol{instance}.png'
        self.warehouse.draw(save=True, filename=filename)

        # Write output
        write_instance(instance, self.warehouse.total_travel_distance if self.warehouse.feasible else math.inf,
                       self.warehouse.get_PA_dimensions())

        # Log final
        if log_to_console:
            print("\r\nFinal solution saved as", filename, "\r\n")

        # Save generations
        if self.save_generations:
            self.generations.to_csv("data/generations/inst" + str(instance) + ".csv")

    def create_random_chromosome(self):
        # Create random order as done in Goncalves
        order = np.random.random_sample(self.N).round(2)

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
        # First generation
        self.generation_number = 0

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
        # Next generation
        self.generation_number = self.generation_number + 1

        # Set fittest size, these are the fraction of the population of fittest chromosomes we select and the fraction of the population of children we make
        self.fittest_size = fittest_size if fittest_size is not None else self.fittest_size
        self.children_size = children_size if children_size is not None else self.children_size

        # Select fittest chromosomes
        fittest = self.select_fittest(int(self.fittest_size * self.population_size))
        fittest_chromosomes = list(map(get_chromosomes, fittest))

        # Create children from fittest chromosomes
        if len(fittest) > 0:
            child_chromosomes = self.create_children(fittest_chromosomes,
                                                     int(self.children_size * self.population_size))
        else:
            child_chromosomes = []

        # Create new population
        self.population = []
        for chromosome, obj_value, feasibility in fittest:
            if not self.population_contains(chromosome):
                # Append to population
                self.add_to_population(chromosome, obj_value=obj_value, feasibility=feasibility, process=False)

        # Add new child chromosomes to population
        for chromosome in child_chromosomes:
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
        str_chromosomes = list(map(get_chromosomes_as_string, self.population))

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
        # Get indexes of which two parents we inherit the order
        if len(chromosomes) > 1:
            # Get random indexes
            indexes = sample(range(len(chromosomes)), 2)

            # Mother is always fittest, father is least fit
            mother_index = min(indexes)
            father_index = max(indexes)
        else:
            # We only have a single parent
            mother_index, father_index = 0, 0

        children = []
        for i in np.arange(size):

            # Decide on mother and father chromosome
            mother, father = chromosomes[mother_index], chromosomes[father_index]

            # Take the average of both parents as the new order
            order = np.array((np.array(mother[:self.N]) + np.array(father[:self.N])) / 2).round(2)

            # Take the number of aisles from the mother or father with 50/50 chance
            aisles = []
            for index in np.arange(self.N, 2 * self.N):
                aisles.append(mother[index] if random() < .5 else father[index])

            # Take the number of cross-aisles from the mother or father with 50/50 chance
            cross_aisles = []
            for index in np.arange(2 * self.N, 3 * self.N):
                cross_aisles.append(mother[index] if random() < .5 else father[index])

            # Create child
            child = [*order, *aisles, *cross_aisles]

            # Mutate child
            child = self.mutate(child)

            # Save generations
            if self.save_generations:
                # Save a tuple of fittest chromosomes and corresponding child chromosomes
                self.generations = self.generations.append(
                    {'generation': self.generation_number, 'mother': '-'.join(str(x) for x in mother),
                     'father': '-'.join(str(x) for x in father), 'child': '-'.join(str(x) for x in child), 'child_no': len(children) + 1},
                    ignore_index=True)

            # Append child
            children.append(child)

        return children

    def mutate(self, chromosome):
        # Mutation
        mutation = random()

        # Change a single aisle
        if .4 < mutation < .8:
            index = randrange(self.N - 1)
            change = 1 if random() < .5 else -1  # Higher chance of increasing aisles
            chromosome[self.N + index] = chromosome[self.N + index] + change
            chromosome[self.N + index] = chromosome[self.N + index] if chromosome[
                                                                           self.N + index] <= self.n_max else self.n_max
            chromosome[self.N + index] = chromosome[self.N + index] if chromosome[self.N + index] >= self.n_min[
                index] else self.n_min[index]

        # Change a single cross-aisle
        if .6 < mutation:
            index = randrange(self.N - 1)
            change = 1 if random() < .50 else -1  # Higher chance of reducing cross-aisles
            chromosome[2 * self.N + index] = chromosome[2 * self.N + index] + change
            chromosome[2 * self.N + index] = chromosome[2 * self.N + index] if chromosome[
                                                                                   2 * self.N + index] <= 10 else 10
            chromosome[2 * self.N + index] = chromosome[2 * self.N + index] if chromosome[
                                                                                   2 * self.N + index] >= 2 else 2

        # Randomly mutate order
        if .2 < mutation < .4:
            order = np.random.random_sample(self.N).round(2)
            chromosome[:self.N] = order

        # Randomly mutate aisles
        if .1 < mutation < .2:
            aisles = chromosome[self.N:2 * self.N]
            aisles_mutation = np.random.randint(-1, 4, size=self.N)
            aisles = np.array(aisles)
            aisles = aisles + aisles_mutation
            aisles[aisles < self.n_min] = self.n_min[aisles < self.n_min]
            aisles[aisles > self.n_max] = self.n_max
            chromosome[self.N:2 * self.N] = aisles

        # Randomly mutate cross-aisles
        if mutation < .1:
            cross_aisles = chromosome[2 * self.N:3 * self.N]
            cross_aisles_mutation = np.random.randint(-1, 2, size=self.N)
            cross_aisles = np.array(cross_aisles)
            cross_aisles = cross_aisles + cross_aisles_mutation
            chromosome[2 * self.N:3 * self.N] = cross_aisles

        # Final check
        aisles = np.array(chromosome[self.N:2 * self.N])
        aisles[aisles < 1] = 1
        aisles[aisles > 30] = 30
        chromosome[self.N:2 * self.N] = aisles
        cross_aisles = np.array(chromosome[2 * self.N:3 * self.N])
        cross_aisles[cross_aisles < 2] = 2
        cross_aisles[cross_aisles > 10] = 10
        chromosome[2 * self.N:3 * self.N] = cross_aisles

        # Return mutated chromosome
        return chromosome

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
