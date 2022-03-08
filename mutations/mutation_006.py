
def mutate_006(self, chromosome):
    # Check feasibility
    obj_value, feasibility = self.warehouse.process(chromosome)

    # If not feasible
    if feasibility is False:
        chromosome[2 * self.N:3 * self.N] = [2 for x in range(self.N)]

    return chromosome
