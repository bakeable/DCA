import numpy as np


def mutate_003(self, chromosome):
    # Randomize order
    order = np.random.random_sample(self.N).round(2)
    chromosome[:self.N] = order

    return chromosome
