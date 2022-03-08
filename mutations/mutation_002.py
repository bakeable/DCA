from random import randrange, random


def mutate_002(self, chromosome):
    index = randrange(self.N - 1)
    change = 1 if random() < .50 else -1  # Higher chance of reducing cross-aisles
    chromosome[2 * self.N + index] = chromosome[2 * self.N + index] + change
    chromosome[2 * self.N + index] = chromosome[2 * self.N + index] if chromosome[
                                                                           2 * self.N + index] <= 10 else 10
    chromosome[2 * self.N + index] = chromosome[2 * self.N + index] if chromosome[
                                                                           2 * self.N + index] >= 2 else 2

    return chromosome