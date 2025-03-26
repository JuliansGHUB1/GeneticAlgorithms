import numpy as np
import random


class NurseSchedulingProblem:
    """Nurse Scheduling Problem with simple availability and streak-based penalties."""

    def __init__(self, hardConstraintPenalty):
        self.hardConstraintPenalty = hardConstraintPenalty
        self.nurses = ['A', 'B', 'C', 'D', 'E']
        self.schedule_length = 160  # fixed length for both availability and schedule
        self.availability = {
            nurse: self.generate_availability()
            for nurse in self.nurses
        }

    def generate_availability(self): ## mock availability generation for each nurse
        # Generate 160-bit string where 1 = unavailable, 0 = available
        return ''.join(str(random.randint(0, 1)) for _ in range(self.schedule_length))

    def getCost(self, scheduleDict):
        """
        scheduleDict: dict where key is nurse, value is 160-bit string of 0s and 1s
        """
        totalCost = 0

        for nurse in self.nurses:
            availability = self.availability[nurse]
            schedule = scheduleDict[nurse]

            for a, s in zip(availability, schedule):
                # Penalize if nurse is scheduled (s=1) but unavailable (a=1)
                if a == '1' and s == '1':
                    totalCost += 1

            # Penalize any 1s in the schedule not part of a streak of at least 4
          ##  totalCost += self.penalize_non_streaks(schedule)

        return self.hardConstraintPenalty * totalCost

    def penalize_non_streaks(self, schedule):
        """
        Penalize all '1's that do not belong to a streak of at least 4
        """
        penalties = 0
        i = 0
        while i < len(schedule):
            if schedule[i] == '1':
                streak_start = i
                while i < len(schedule) and schedule[i] == '1':
                    i += 1
                streak_len = i - streak_start
                if streak_len < 4:
                    penalties += streak_len  # penalize every 1 in this short streak - maybe change this to penalzie distance to nearest multiple of 8
            else:
                i += 1
        return penalties

    def printScheduleInfo(self, scheduleDict):
        for nurse in self.nurses:
            print(f"Nurse {nurse}:")
            print(f"  Availability: {self.availability[nurse]}")
            print(f"  Schedule:     {scheduleDict[nurse]}")
            print()

def visualize_schedule_violations(scheduleDict, nsp):
    num_nurses = len(nsp.nurses)
    slots = nsp.schedule_length
    matrix = np.zeros((num_nurses, slots))

    for i, nurse in enumerate(nsp.nurses):
        schedule = scheduleDict[nurse]
        availability = nsp.availability[nurse]

        for j in range(slots):
            if availability[j] == '1' and schedule[j] == '1':
                matrix[i][j] = 1  # violation (red)
            else:
                matrix[i][j] = 0  # valid (green)

    # Create the heatmap
    plt.figure(figsize=(16, 3))
    plt.imshow(matrix, cmap='RdYlGn_r', aspect='auto')
    plt.colorbar(label="Violation (1 = Red, 0 = Green)")
    plt.yticks(ticks=np.arange(num_nurses), labels=nsp.nurses)
    plt.xlabel("Time Slots (0–159)")
    plt.title("Nurse Schedule vs. Availability Violations")
    plt.tight_layout()
    plt.show()

# Testing the class:
def main():
    nurses = NurseSchedulingProblem(hardConstraintPenalty=10)

    # Generate a random schedule: 160-bit string of 0s and 1s per nurse
    np.random.seed(42)
    scheduleDict = {
        nurse: ''.join(str(bit) for bit in np.random.randint(2, size=160))
        for nurse in nurses.nurses
    }

    nurses.printScheduleInfo(scheduleDict)
    print("Total Cost =", nurses.getCost(scheduleDict))

    visualize_schedule_violations(scheduleDict, nsp)


if __name__ == "__main__":
    main()
