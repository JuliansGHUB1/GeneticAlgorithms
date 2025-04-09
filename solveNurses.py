from deap import base
from deap import creator
from deap import tools

import random
import numpy

import matplotlib.pyplot as plt
import seaborn as sns

import nurses

import sys
import elitism

INDIVIDUAL_SIZE = 800

# problem constants:
HARD_CONSTRAINT_PENALTY = 1   # the penalty factor for a hard-constraint violation

# Genetic Algorithm constants:
POPULATION_SIZE = 300
P_CROSSOVER = 0.9  # probability for crossover
P_MUTATION = 0.1   # probability for mutating an individual
MAX_GENERATIONS = 1000
HALL_OF_FAME_SIZE = 30

# set the random seed:
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

toolbox = base.Toolbox()

# create the nurse scheduling problem instance to be used:
nsp = nurses.NurseSchedulingProblem(HARD_CONSTRAINT_PENALTY)

# define a single objective, maximizing fitness strategy:
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

# create the Individual class based on list:
creator.create("Individual", list, fitness=creator.FitnessMin)

# create an operator that randomly returns 0 or 1:
toolbox.register("zeroOrOne", random.randint, 0, 1)

# create the individual operator to fill up an Individual instance:
# toolbox.register("individualCreator", tools.initRepeat, creator.Individual, toolbox.zeroOrOne, 800)

# create the population operator to generate a list of individuals:
# toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)

# Calculate the string for a 32 bit day where we model a day in a schedule as follows:
# You work on this day with probablility random.randint(0,1) and if you do work on this day
# then you will start work at index a where a [0, 31] and you will continue to work until
# b which is uniformly picked from [1, max hours = 32 - a // 4 ]. The reason we modeled
# it this way is because we are trying to generate candidate solutions and candidate solutions
# should appear like viable solutions. You would believe that a viable schedule for a day
# essentially has some probability of the person working on that day and if that person
# is working on that day then the specific block of time they work occurs with some probability
# To build a complete individual I would concatenate 25 such strings, bc 1 day * 5 days * 5 nurses
def smart_block():
    flip = random.randint(0, 1)
    if flip == 0:
        return [0] * 32  # All zeros (off for the day)

    a = random.randint(0, 31)
    max_hours = (32 - a) // 4  # Max full hours we can fit starting at a
    if max_hours == 0:
        return [0] * 32  # Not enough room for 1 hour, so skip

    b = random.randint(1, max_hours)  # Duration in hours
    length = b * 4  # Convert hours to number of 15-minute blocks
    shift = [0] * a + [1] * length + [0] * (32 - (a + length))
    return shift

# Calculate an INDIVIDUAL - i.e. the initial population of
# candidate solutions which will be each of length 600 
# as we have 5 nurses, 5 days, 32 15-increments per day
def smart_individual():
    individual = []
    for _ in range(25):  # 25 blocks * 32 bits = 800 bits
        individual.extend(smart_block())
    return creator.Individual(individual)



def island_expand_mutation(individual, expansion_prob=0.3, max_expansions=2):
    new_individual = individual[:]
    islands = []

    # Step 1: Find all islands (streaks of 1s of length >= 4)
    i = 0
    while i < len(new_individual):
        if new_individual[i] == 1:
            start = i
            while i < len(new_individual) and new_individual[i] == 1:
                i += 1
            end = i
            if end - start >= 4:
                islands.append((start, end))
        else:
            i += 1

    # Step 2: Select a few islands at random to expand
    selected = random.sample(islands, min(len(islands), max_expansions))
    for start, end in selected:
        probabilityToExpandIsland = random.random() < expansion_prob
        if probabilityToExpandIsland and start > 0:
            new_individual[start - 1] = 1
        if probabilityToExpandIsland and end < len(new_individual): 
            new_individual[end] = 1

    return new_individual


toolbox.register("individualCreator", smart_individual)
toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)



# Obtains the cost of a candidate solution. A candidate solution is the concatenation of nurses
# schedules, where the first 160 bits is Nurse A's schedule, the next 160 bits is nurse B's schedule and so on
# for the entire 800 length schedule which is for 5 nurses. The cost of a candidate solution is higher when
# it violates more constraints and lower when it violates less constraints, so it is a sort of measure of 
# fitness from the perspective of the evolutionary algorithm.
def getCost(individual):
    scheduleDict = {}
    bits_per_nurse = nsp.schedule_length
    # For each nurse, first obtain her individual schedule from the candidate solution (concat. of all nurses schedules)
    # For example, for nurse A, get the substring [0, 159] for nurse B [160, 319] and so on
    # For each nurse-schedule pair add it to a map to get <nurse, schedule> mapping
    # getCost of this candidate schedule
    for idx, nurse in enumerate(nsp.nurses): # (nurses is an array of Nurses where each index is an identifier for a nurse - "A", "B", etc.)
        start = idx * bits_per_nurse 
        end = start + bits_per_nurse
        bitstring = ''.join(str(b) for b in individual[start:end])
        scheduleDict[nurse] = bitstring

    return nsp.getCost(scheduleDict),


toolbox.register("evaluate", getCost)

# genetic operators:
toolbox.register("select", tools.selTournament, tournsize=2)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=1.0/INDIVIDUAL_SIZE)


def individualToScheduleDict(individual, nurses, schedule_length):
    scheduleDict = {}
    for idx, nurse in enumerate(nurses):
        start = idx * schedule_length
        end = start + schedule_length
        bitstring = ''.join(str(b) for b in individual[start:end])
        scheduleDict[nurse] = bitstring
    return scheduleDict

# Genetic Algorithm flow:
def main():

    # create initial population (generation 0):
    population = toolbox.populationCreator(n=POPULATION_SIZE)

    # prepare the statistics object:
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", numpy.min)
    stats.register("avg", numpy.mean)

    # define the hall-of-fame object:
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # perform the Genetic Algorithm flow with hof feature added:
    population, logbook = elitism.eaSimpleWithElitism(population, toolbox, cxpb=P_CROSSOVER, mutpb=P_MUTATION,
                                              ngen=MAX_GENERATIONS, stats=stats, halloffame=hof, verbose=True)

    # print best solution found:
    best = hof.items[0]
    print("-- Best Individual = ", best)
    print("-- Best Fitness = ", best.fitness.values[0])
    print()
    print("-- Schedule = ")
    # Convert best individual to proper schedule dictionary
    scheduleDict = individualToScheduleDict(best, nsp.nurses, nsp.schedule_length)

    # Now print it properly
    nsp.printScheduleInfo(scheduleDict)

    # Print its statistics
    total_incomplete_streaks = 0
    for nurse in nsp.nurses:
        schedule = scheduleDict[nurse]
        total_incomplete_streaks += nsp.number_of_incomplete_streaks(schedule, len(schedule))
    
    
    print("Total incomplete streaks for 'best' individual we evolved:", total_incomplete_streaks)

    availability_violations = nsp.getNumAvailabilityViolations(scheduleDict)
    print("Total availability violations for best individual evolved:", availability_violations)

    # extract statistics:
    minFitnessValues, meanFitnessValues = logbook.select("min", "avg")

    # plot statistics:
    sns.set_style("whitegrid")
    plt.plot(minFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Min / Average Fitness')
    plt.title('Min and Average fitness over Generations')
    plt.show()


if __name__ == "__main__":
    main()