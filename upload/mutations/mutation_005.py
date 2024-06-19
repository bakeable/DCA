import numpy as np


def mutate_005(self, chromosome):
    cross_aisles = chromosome[2 * self.N:3 * self.N]
    cross_aisles_mutation = np.random.randint(-1, 2, size=self.N)
    cross_aisles = np.array(cross_aisles)
    cross_aisles = cross_aisles + cross_aisles_mutation
    chromosome[2 * self.N:3 * self.N] = cross_aisles

    return chromosome
