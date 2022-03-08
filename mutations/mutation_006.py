
def mutate_006(self, chromosome):
    # Check feasibility
    obj_value, feasibility = self.warehouse.process(chromosome)

    # If not feasible
    if feasibility is False:
        print("Not feasible!")

    return chromosome
