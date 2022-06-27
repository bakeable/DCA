import math
from random import random, randrange, sample
import numpy as np
from classes import Warehouse
from functions import read_instance, write_instance
from tqdm import tqdm
import pandas as pd
from mutations import mutations
from datetime import datetime
from generate_feasible_solutions import generate_feasible_solutions
from matplotlib import pyplot as plt
import os


def get_chromosomes(tup):
    return tup[0]


def get_chromosomes_as_string(tup):
    return "-".join(str(x) for x in tup[0])


class GeneticAlgorithm:
    def __init__(self, population_size=50, iterations=30, fittest_size=.2, children_size=.5, save_generations=False, log_to_console=True):
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

        # Settings
        self.enable_diagnostics = False
        self.log_to_console = log_to_console

        # Mutation distribution
        self.mutation_names = ['001', '002', '003', '004', '005', '006', '008', '009']
        self.original_mutation_probs = [.05, .05, .2, .15, .15, .1, .1, .2]
        self.mutation_probs = self.original_mutation_probs
        self.mutation_points = [20] * len(self.mutation_names)
        self.mutation_occurences = [0 for x in self.mutation_names]

    def instantiate(self, instance):
        # Read variables from instance
        W, H, N, w_i, v_i, S, alpha, u, mean_u = read_instance(instance)

        # Instantiate warehouse
        self.warehouse = Warehouse(W, H, S, u, alpha, animate=False, w_i=w_i, v_i=v_i)

        # Instantiate variables
        self.N = N
        self.n_min, self.k_min, self.n_max, self.k_max = self.warehouse.n_min, self.warehouse.k_min, self.warehouse.n_max, self.warehouse.k_max

    def run(self, instance, allow_infeasible_parents=False):
        # Diagnostics
        global iterStartTime
        run_diagnostics = []

        # Instantiate
        self.instantiate(instance)
        if self.log_to_console:
            print("Instance instantiated")

        # Create initial population
        self.create_initial_population(min_feasible=int(self.fittest_size * self.population_size))  # We should at least have a mother and a father

        # Iterate
        last_improvement = 0
        while last_improvement < 1:
            # Increment time from last improvement
            last_improvement = last_improvement + 1

            # Keep track of improvement
            total_improved = 0
            prev_fittest_obj_value = self.fittest_obj_value

            # Log
            if self.log_to_console:
                print("Starting new set of iterations\r\n")

            for i in tqdm(range(self.iterations)):
                # Get diagnostics
                if self.enable_diagnostics:
                    iterStartTime = datetime.now()

                # Create next population
                self.create_next_population(allow_infeasible_parents=allow_infeasible_parents)

                # Set fittest objective value
                fittest = self.select_fittest(1)
                if len(fittest) > 0:
                    if self.fittest_obj_value > fittest[0][1]:
                        self.obj_value_decrease = self.fittest_obj_value - fittest[0][1]
                        total_improved = total_improved + self.obj_value_decrease
                        self.fittest_obj_value = fittest[0][1]
                        last_improvement = 0

                # Diagnostics
                if self.enable_diagnostics:
                    run_diagnostics.append({
                        'generation': self.generation_number,
                        'time': datetime.now() - iterStartTime,
                        'feasible_solutions': len(self.get_feasible_solutions()),
                        'obj_value': self.fittest_obj_value
                    })

            # Log
            if self.log_to_console:
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
            if self.log_to_console:
                print("\r\nA feasible solution was found")
                print("Optimal chromosome:", solution[0])
                print("Total distance:", solution[1])
                print("PA layout:", self.warehouse.get_PA_dimensions())
                if self.enable_diagnostics:
                    print("Total runtime:", sum([int(x['time'].total_seconds() * 1000) for x in run_diagnostics]), "ms")
                    print("Average iteration time:",
                          np.mean([int(x['time'].total_seconds() * 1000) for x in run_diagnostics]), "ms")
                    print("Average number of feasible solutions every iteration:",
                          np.mean([x['feasible_solutions'] for x in run_diagnostics]))

        else:
            # Log
            if self.log_to_console:
                print("\r\nAlgorithm did not find a feasible solution")

            # Take best infeasible
            solution = self.select_fittest(1, allow_infeasible=True)[0]

        # Process solution
        self.warehouse.process(solution[0])
        self.warehouse.draw()

        # Draw solution as a PNG
        filename = f'output/sol{instance}.png'
        self.warehouse.draw(save=True, filename=filename)

        # Write output
        write_instance(instance, self.warehouse.total_travel_distance if self.warehouse.feasible else -1,
                       self.warehouse.get_PA_dimensions())

        # Log final
        if self.log_to_console:
            print("\r\nFinal solution saved as", filename, "\r\n")

        # Save generations
        if self.save_generations:
            self.generations.to_csv("data/generations/inst" + str(instance) + ".csv")

        # Diagnostics
        if self.enable_diagnostics:
            # Get x and y
            generations = [x['generation'] for x in run_diagnostics]
            objective_value = [x['obj_value'] for x in run_diagnostics]

            # Create folder to save diagnostics
            if not os.path.isdir(f'data/diagnostics/instance{instance}'):
                os.mkdir(f'data/diagnostics/instance{instance}')

            # Collect diagnostics
            elite_size = round(self.population_size * self.fittest_size)
            children_size = round(self.population_size * self.children_size)
            iteration_time = round(np.mean([int(x['time'].total_seconds() * 1000) for x in run_diagnostics]))
            total_time = sum([int(x['time'].total_seconds() * 1000) for x in run_diagnostics])

            # Save data
            try:
                df = pd.read_csv(f'data/diagnostics/instance{instance}/diagnostics.csv')
            except:
                df = pd.DataFrame(
                    columns=["population_size", "elite_size", "children_size", "iteration_time", "total_time",
                             "number_of_generations", "objective_value", "chromosome", "mutation_probs",
                             "mutation_names", "generations_progress", "objective_value_progress"])
            # Append row
            df = df.append({
                "population_size": self.population_size,
                "elite_size": elite_size,
                "children_size": children_size,
                "iteration_time": iteration_time,
                "iterations_per_set": self.iterations,
                "total_time": total_time,
                "number_of_generations": self.generation_number,
                "objective_value": solution[1],
                "chromosome": "|".join([str(x) for x in solution[0]]),
                "mutation_probs": "|".join([str(x) for x in self.original_mutation_probs]),
                "mutation_occurences": "|".join([str(x) for x in self.mutation_occurences]),
                "mutation_names": "|".join(self.mutation_names),
                "generations_progress": "|".join([str(x) for x in generations]),
                "objective_value_progress": "|".join([str(x) for x in objective_value])
            }, ignore_index=True)

            # Save diagnostics
            df.to_csv(f'data/diagnostics/instance{instance}/diagnostics.csv', index=False)

            # Get length of rows
            diagnostic_entry = len(df)

            # Create figure
            plt.figure()

            # Get axis
            plt.plot(generations, objective_value)

            # Add text
            string = "Objective value: " + str(solution[1]) + "\n" + \
                     "Population size: " + str(self.population_size) + "\n" + \
                     "Elite size: " + str(elite_size) + "\n" + \
                     "Children size: " + str(children_size) + "\n" + \
                     "Iteration time: " + str(iteration_time) + "ms\n" + \
                     "Total time: " + str(total_time) + "ms\n" + \
                     "Number of generations: " + str(self.generation_number) + "\n"
            plt.text(0.5, .98, string, fontsize=12, horizontalalignment='left', verticalalignment='top',
                     transform=plt.gca().transAxes)

            # Set title
            plt.title("Objective value over generations")
            plt.xlabel("Number of generations")
            plt.ylabel("Objective value")

            # Save plot
            filename = f'data/diagnostics/instance{instance}/diagnostic_entry_{str(diagnostic_entry)}.png'
            plt.savefig(filename)
            plt.show()

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
        # Log to console
        if self.log_to_console:
            print("Creating initial population")

        # First generation
        self.generation_number = 0

        # Create random chromosomes
        feasible = 0
        total_generated_chromosomes = 0
        feasible_generator_used = False
        while len(self.population) < self.population_size:
            total_generated_chromosomes = total_generated_chromosomes + 1

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
            elif total_generated_chromosomes > (self.population_size * 10) and not feasible_generator_used:
                # Log to console
                if self.log_to_console:
                    print("No feasible solutions found as of yet, trying to generate them systematically")

                # Generate feasible chromosomes
                feasible_solutions = generate_feasible_solutions(algorithm=self, max_solutions=self.population_size, max_run_time=300)
                feasible_generator_used = True

                # Log to console
                if self.log_to_console and len(feasible_solutions) == 0:
                    print("Could not find enough feasible solutions, adding random chromosomes instead")

                # Append to population
                for solution in feasible_solutions:
                    if len(self.population) < self.population_size:
                        # Unpack
                        chromosome, obj_value, feasibility = solution

                        # Add to population
                        self.add_to_population(chromosome, obj_value=obj_value, feasibility=feasibility)

                        # Number of feasible items
                        feasible = feasible + 1

            # Fill with random chromosomes
            if feasible_generator_used:

                # Add to population
                self.population.append(item)

    def create_next_population(self, fittest_size=None, children_size=None, allow_infeasible_parents=False):
        # Next generation
        self.generation_number = self.generation_number + 1

        # Set fittest size, these are the fraction of the population of fittest chromosomes we select and the fraction of the population of children we make
        self.fittest_size = fittest_size if fittest_size is not None else self.fittest_size
        self.children_size = children_size if children_size is not None else self.children_size

        # Select fittest chromosomes
        fittest = self.select_fittest(int(self.fittest_size * self.population_size),
                                      allow_infeasible=allow_infeasible_parents)
        fittest_chromosomes = list(map(get_chromosomes, fittest))

        # Create children from fittest chromosomes
        if len(fittest) > 0:
            children = self.create_children(fittest_chromosomes,
                                                     int(self.children_size * self.population_size))
        else:
            children = []

        # Create new population
        self.population = []
        for chromosome, obj_value, feasibility in fittest:
            if not self.population_contains(chromosome):
                # Append to population
                self.add_to_population(chromosome, obj_value=obj_value, feasibility=feasibility, process=False)

        # Add new child chromosomes to population
        for chromosome, obj_value, feasibility in children:
            if not self.population_contains(chromosome):
                # Append to population
                self.add_to_population(chromosome, obj_value=obj_value, feasibility=feasibility, process=False)

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
        children = []
        for i in np.arange(size):
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
            child_chromosome = [*order, *aisles, *cross_aisles]

            # Mutate child
            pre_mutated_child = [*order, *aisles, *cross_aisles]
            mutated_chromosome, mutation_name = self.mutate(child_chromosome)

            # Evaluate child
            obj_value, feasibility = self.warehouse.process(mutated_chromosome)

            # Mutation points
            if self.fittest_obj_value < obj_value and self.mutation_points[self.mutation_names.index(mutation_name)] < 100:
                self.mutation_points[self.mutation_names.index(mutation_name)] = self.mutation_points[self.mutation_names.index(mutation_name)] + 1
            elif self.fittest_obj_value > obj_value and self.mutation_points[self.mutation_names.index(mutation_name)] > 0:
                self.mutation_points[self.mutation_names.index(mutation_name)] = self.mutation_points[self.mutation_names.index(mutation_name)] - 1

            # Save generations
            if self.save_generations:
                # Calculate mutations
                mutation = np.array(np.array(pre_mutated_child) - np.array(mutated_chromosome)).round(2)

                # Save a tuple of fittest chromosomes and corresponding child chromosomes
                self.generations = self.generations.append(
                    {'generation': self.generation_number, 'mother': '|'.join(str(x) for x in mother),
                     'father': '|'.join(str(x) for x in father), 'child': '|'.join(str(x) for x in child_chromosome),
                     'mutation_name': mutation_name, 'obj_value': str(obj_value), 'feasibility': str(feasibility),
                     'mutation': '|'.join(str(x) for x in mutation), 'child_no': len(children) + 1},
                    ignore_index=True)

            # Append child
            children.append((mutated_chromosome, obj_value, feasibility))

        return children

    def mutate(self, chromosome):
        # Get which mutation to apply
        total_mutation_points =sum(self.mutation_points)
        mutation_probs = [x / total_mutation_points for x in self.mutation_points]
        mutation_name = str(np.random.choice(self.mutation_names, 1, mutation_probs)[
                                0])  # Chooses a random mutation according to the specified distribution
        mutation_function = mutations[mutation_name]

        # Keep diagnostics
        if self.enable_diagnostics:
            self.mutation_occurences[self.mutation_names.index(mutation_name)] = self.mutation_occurences[self.mutation_names.index(mutation_name)] + 1

        # Mutate chromosome
        chromosome = mutation_function(self, chromosome)  # Runs the mutation

        # Final check for absolute maximum of aisles and cross-aisles
        aisles = np.array(chromosome[self.N:2 * self.N])
        aisles[aisles < 1] = 1
        aisles[aisles > 30] = 30
        chromosome[self.N:2 * self.N] = aisles
        cross_aisles = np.array(chromosome[2 * self.N:3 * self.N])
        cross_aisles[cross_aisles < 2] = 2
        cross_aisles[cross_aisles > 10] = 10
        chromosome[2 * self.N:3 * self.N] = cross_aisles

        # Return mutated chromosome
        return (chromosome, mutation_name)

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
