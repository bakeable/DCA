import numpy as np


def mutate_004(self, chromosome):
    aisles = chromosome[self.N:2 * self.N]
    aisles_mutation = np.random.randint(-1, 4, size=self.N)
    aisles = np.array(aisles)
    aisles = aisles + aisles_mutation
    aisles[aisles < self.n_min] = self.n_min[aisles < self.n_min]
    aisles[aisles > self.n_max] = self.n_max
    chromosome[self.N:2 * self.N] = aisles
    return chromosome
