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

from solveNurses import smart_individual

# 10 students, fit their availability - minimize streaks

def main():
    maxHours = 2

    studentDict = {}
    for i in range(10):
        bit_string = ''.join(random.choice('01') for _ in range(16))  # Availability Strings
        studentDict[str(i)] = bit_string
    
    # Assume 1 available and 0 is unavailable
    # Working is 1 0 is not working
    

    negation_str = ""

    for key, bit_string in studentDict:
        count = 0
        for i in range (len(bit_string)):
            if (bit_string[i] == "0"):
                count = count + 1
                if ( count == 2): 

                
                else:
                    negation_str += "1"
                
            else:
                negation_str += "0"



            
    









    