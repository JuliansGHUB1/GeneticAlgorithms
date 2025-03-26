import random
from deap import base, creator, tools, algorithms

# 1. Define the fitness and individual
creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # Maximize
creator.create("Individual", list, fitness=creator.FitnessMax)

# 2. Set up the toolbox
toolbox = base.Toolbox()
toolbox.register("attr_bool", random.randint, 0, 1)  # Generate one bit
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 4)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# 3. Fitness function: count number of 1s
def evalOnes(individual):
    return sum(individual),  # DEAP needs a tuple

toolbox.register("evaluate", evalOnes)
toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.1)  # 10% chance per bit
toolbox.register("select", tools.selTournament, tournsize=2)

# 4. Run the GA
def main():
    pop = toolbox.population(n=10)  # Small population
    
    print("Initial Population:")
    for i, ind in enumerate(pop):
        print(f"Individual {i}: {ind}")





    hof = tools.HallOfFame(1)       # Best individual
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", lambda x: sum(v[0] for v in x) / len(x))
    stats.register("max", lambda x: max(v[0] for v in x))

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.3,
                                   ngen=10, stats=stats, halloffame=hof, verbose=True)

    print("\nBest 4-bit individual:", hof[0])
    print("With fitness:", hof[0].fitness.values[0])

if __name__ == "__main__":
    main()