from random import random, randrange


def mutate_001(self, chromosome):
    index = randrange(self.N - 1)
    change = 1 if random() < .75 else -1  # Higher chance of increasing aisles
    chromosome[self.N + index] = chromosome[self.N + index] + change
    chromosome[self.N + index] = chromosome[self.N + index] if chromosome[self.N + index] <= self.n_max else self.n_max
    chromosome[self.N + index] = chromosome[self.N + index] if chromosome[self.N + index] >= self.n_min[
        index] else self.n_min[index]

    return chromosome
