import numpy as np
import random


class NurseSchedulingProblem:
    """Nurse Scheduling Problem with simple availability and streak-based penalties."""

    # This is the constructor for NurseSchedulingProblem objects, which encapsulate the data
    # about the problem such as the hardConstraintPenalty, each nurse's 'id' or 'name' is saved
    # in a nurses array, the length of the schedule is fixed within here and there is a mapping
    # known as availability which maps nurses to their availability string (a string describing
    # when they are free or not free))
    def __init__(self, hardConstraintPenalty):
        self.hardConstraintPenalty = hardConstraintPenalty # The penalty of violating a hardconstraint is 10x as severe as soft
        self.nurses = ['A', 'B', 'C', 'D', 'E'] # We enumerate each nurse with a letter
        self.schedule_length = 160  # length of a single individual's schedule/availability
        self.availability = { # A mapping from each nurse to their availability, which at the moment is randomly generated
            nurse: self.generate_block_availability() # Notice that currently we have 5 nurses, and for each the availability is randomly gen.
            for nurse in self.nurses
        }

    # A function that generates a random string of length schedule_length (160) to represent an individual nurses availability
    def generate_availability(self): 
        return ''.join(str(random.randint(0, 1)) for _ in range(self.schedule_length))

    # A function that generates a random string of schedule length = 160 but using the idea that peoples time is more in a 
    # block fashion where they are either busy or free for blocks [1,4] hours
    # Generates one single nurses's availability for the entire week in a 15 minute encoding
    def generate_block_availability(self):

        producedString = 0 # The amount of the string you've produced thus far

        availabilityString = ""
        while(producedString < self.schedule_length):
            block_length = random.randint(1,4) # The standard block of time people are free/busy for is on [1,4] hours
            block_availability = random.randint(0, 1) # Now that we have the length of the block, we need whether they are free or not
            number_bits_to_add = block_length * 4 # converts the block in hours to 15 minute increments as our string encoding is in 15 minute increments
            availabilityString += (str(block_availability) * number_bits_to_add)
            producedString = len(availabilityString)
        
        availabilityString = availabilityString[:160]  ## in case you overfilled
        return availabilityString



    
    def getCost(self, scheduleDict):
        sumHardConstraints = self.getNumAvailabilityViolations(scheduleDict) # Add to hc violations the number of availability violations (schedule when unavailable)
        
        lessThanHourLongShiftPenalty = 0
        for schedule in scheduleDict.values(): 
            lessThanHourLongShiftPenalty += self.penalize_non_streaks(schedule, len(schedule)) # Add to hc violations the number of shifts < 1 hour long
        
        sumSoftConstraints = 0 # Currently no soft constraints yet

        return 5  * sumHardConstraints + lessThanHourLongShiftPenalty # 10 is too conservative, 0 not conservative enough

    # Function takes each nurse's schedule in valueset of scheduleDict and compares to the nurse's availability string
    # and counts the total number of times a nurse is scheduled when she is unavailable
    # Function returns number of violations in schedules of each nurse, where a violation
    # is a time slot during which a nurse is scheduled to work but is unavailable 
    def getNumAvailabilityViolations(self, scheduleDict):
        totalCost = 0

        for nurse in self.nurses: # For each nurse
            availability = self.availability[nurse] # get its availability from (nurse, availability string) map
            schedule = scheduleDict[nurse] # obtain the corresponding schedule from (nurse, schedule) map passed as parameter

            for a, s in zip(availability, schedule):
                # If for any nurse's availability string there is a 1 at some index, and there is a 1 at the corresponding
                # index in the nurses schedule, we must add 1 to the total cost bc this represents a time when a nurse
                # is scheduled to work when they are unavailable
                if a == '1' and s == '1':
                    totalCost += 1

        # Here, the totalCost = number of schedule violations. Since this is hard constraint violation
        # As opposed to a soft constraint violation, we penalize them harsher by multiplying by some coeffecient
        # known as the hardConstraintPenalty
        return totalCost

    # Takes a string of length n and then for each occurence of a run of 1's less than 4, it will sum the penalization function
    # applied on each such occurence
    # Use case: Given a schedule we want to penalize less than 4 consecutive 1's,
    # as in a scheduling's encoding scheme less than 4 consecutive 1's means a shift less than 1 hour,
    # which violates a hard constraint. Algorithm identifies each run of 1's and checks if its less than 4 and increments count if it is
    def penalize_non_streaks(self, schedule, n):
        n = len(schedule)
        ptr1 = 0 # Demarcates the start of windows of streaks
        ptr2 = 0 # Is an iteration variable
        inStreak = False; # Boolean to represent whether we are in a streak or not
        violationCount = 0 # Number of times in a individual persons schedule that they are scheduled for less than an hour (4 15 minute increments)
        minConsecutiveBits = 4 # At minimum you must be scheduled for an hour - 4 15 minute increments
        while(ptr2 <= n):
            # Only 3 cases to consider: at x = n - 1, in a streak that continues as A[n-1] = 1 ; in a streak that ends as A[n-1] = 0;
            # in a streak that starts at n - 1. In the middle case the streak length will be calculated in iteration where p = n-1
            # However, in the other two cases we must have one extra iteration to get streak length
            if(ptr2 == n): # Case for when a streak started at n - 1 or perhaps a streak continued from some [p1, n-1]
                    if(inStreak):
                        lengthOfStreak = n - ptr1
                        isViolation = lengthOfStreak < minConsecutiveBits
                        if(isViolation):
                            distanceToNoStreak = lengthOfStreak # we can correct this by removing all the 1s
                            violationCount = violationCount + (minConsecutiveBits - lengthOfStreak) ** 2
            
                    break ## Whether or not if we are inStreak is true, we have completely exhausted the string searching for runs of 4 consecutive 1s, so break

            startNewStreak = (not inStreak) and schedule[ptr2] == "1"
            endOfStreak = inStreak and schedule[ptr2] == "0"
            if(startNewStreak):
                ptr1 = ptr2 # this index is the start of a streak of 1s of at least length 1
                inStreak = True # we are now in  a streak
            elif(endOfStreak):
                # Case where we had a run from [ptr1, ptr2) of 1s
                lengthOfStreak = ptr2 - ptr1
                isViolation = lengthOfStreak < minConsecutiveBits
                if(isViolation):
                     violationCount = violationCount + (minConsecutiveBits - lengthOfStreak) ** 2
                
                inStreak = False # we are no longer in a streak
            
            ptr2 = ptr2 + 1 # Increment iteration variable
        return violationCount
    
    # Takes a string of length n and then counts the number of occurences of runs of 1s of length less than 4
    # Useful for contextualizing the results of a run of the algorithm, because you can see the true number of violations
    def number_of_incomplete_streaks(self, schedule, n):
        n = len(schedule)
        ptr1 = 0 # Demarcates the start of windows of streaks
        ptr2 = 0 # Is an iteration variable
        inStreak = False; # Boolean to represent whether we are in a streak or not
        violationCount = 0 # Number of times in a individual persons schedule that they are scheduled for less than an hour (4 15 minute increments)
        minConsecutiveBits = 4 # At minimum you must be scheduled for an hour - 4 15 minute increments
        while(ptr2 <= n):
            # Only 3 cases to consider: at x = n - 1, in a streak that continues as A[n-1] = 1 ; in a streak that ends as A[n-1] = 0;
            # in a streak that starts at n - 1. In the middle case the streak length will be calculated in iteration where p = n-1
            # However, in the other two cases we must have one extra iteration to get streak length
            if(ptr2 == n): # Case for when a streak started at n - 1 or perhaps a streak continued from some [p1, n-1]
                    if(inStreak):
                        lengthOfStreak = n - ptr1
                        isViolation = lengthOfStreak < minConsecutiveBits
                        if(isViolation):
                           violationCount = violationCount + 1
            
                    break ## Whether or not if we are inStreak is true, we have completely exhausted the string searching for runs of 4 consecutive 1s, so break

            startNewStreak = (not inStreak) and schedule[ptr2] == "1"
            endOfStreak = inStreak and schedule[ptr2] == "0"
            if(startNewStreak):
                ptr1 = ptr2 # this index is the start of a streak of 1s of at least length 1
                inStreak = True # we are now in  a streak
            elif(endOfStreak):
                # Case where we had a run from [ptr1, ptr2) of 1s
                lengthOfStreak = ptr2 - ptr1
                isViolation = lengthOfStreak < minConsecutiveBits
                if(isViolation):
                     violationCount = violationCount + 1
                
                inStreak = False # we are no longer in a streak
            
            ptr2 = ptr2 + 1 # Increment iteration variable
        return violationCount
                

            

      

    # Prints the schedule of every nurse by using a map from (nurses, schedule string)
    def printScheduleInfo(self, scheduleDict):
        for nurse in self.nurses:
            print(f"Nurse {nurse}:")
            print(f"  Availability: {self.availability[nurse]}")
            print(f"  Schedule:     {scheduleDict[nurse]}")
            print()


def main():
    # Here I am instantiating a nurseSchedulingProblem isntance with a hardConstraintPenalty of 10
    # Internally, this will produce nurses (hardcoded to be 5 at the moment) and a randomly generated
    # schedule for each nurse.
    nurses = NurseSchedulingProblem(hardConstraintPenalty=10)

    # Here, for each nurse, we are generating a random schedule of length 160, and then creating a map
    # from (nurse, randomlygeneratedschedulefornurse). This is done in an efforts to experiment with
    # what the cost will be for a randomly generated schedule (which we predict will be quite high)
    np.random.seed(42)
    scheduleDict = {
        nurse: ''.join(str(bit) for bit in np.random.randint(2, size=160))
        for nurse in nurses.nurses
    }

    nurses.printScheduleInfo(scheduleDict) # Prints the schedules of each nurse
    # gets the cost of the randomly generated schedule, which we will see is quite high
    print("Total Cost =", nurses.getCost(scheduleDict)) 


if __name__ == "__main__":
    main()
