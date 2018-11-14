# pacmanAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from pacman import Directions
from game import Agent
from heuristics import *
import random
import math

class RandomAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        return

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # get all legal actions for pacman
        actions = state.getLegalPacmanActions()
        # returns random action from all the valide actions
        return actions[random.randint(0,len(actions)-1)]

class RandomSequenceAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        self.actionList = []
        for i in range(0,10):
            self.actionList.append(Directions.STOP)
        return

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # get all legal actions for pacman
        possible = state.getAllPossibleActions()
        for i in range(0,len(self.actionList)):
            self.actionList[i] = possible[random.randint(0,len(possible)-1)]
        tempState = state
        for i in range(0,len(self.actionList)):
            if tempState.isWin() + tempState.isLose() == 0:
                tempState = tempState.generatePacmanSuccessor(self.actionList[i])
            else:
                break
        # returns random action from all the valide actions
        return self.actionList[0]

class HillClimberAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        # Action Sequence are of length 5
        self.actionList = []
        for i in range(0, 5):
            self.actionList.append(Directions.STOP)
        return

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # get all legal actions for pacman
        possible = state.getAllPossibleActions()
        for i in range(0, len(self.actionList)):
            self.actionList[i] = random.choice(possible)

        # keep tracking best action list and its score
        bestScore = float('-inf')
        bestActionList = self.actionList[:] # get a copy

        while True:
            currState = state
            currScore = gameEvaluation(state, currState)
            for i in range(0, len(self.actionList)):
                # if the state is a win/lose state, break
                if currState.isWin():
                    break
                if currState.isLose():
                    break
                # apply this action to curr state
                currState = currState.generatePacmanSuccessor(self.actionList[i])
                if not currState:
                    break
                else:
                    # update score
                    currScore = gameEvaluation(state, currState)
            if currScore > bestScore:
                bestScore = currScore
                bestActionList = self.actionList[:] # get a copy
            # Each action in the sequence has 50% chance to be changed into random action.
            if not currState:
                break
            possible = currState.getAllPossibleActions()
            for i in range(0, len(self.actionList)):
                if random.randint(0, 1) == 1:
                    self.actionList[i] = random.choice(possible)

        return bestActionList[0]

class GeneticAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        return

    def selection(self, chromosomes):
        n = len(chromosomes)
        total = n * (n + 1) // 2 # sum: n + (n - 1) + ... + 1
        rand = random.randint(1, total)
        # print total, rand
        sum = 0
        for i in range(0, n):
            sum += (n - i)
            if sum >= rand:
                return chromosomes[i]
        return None

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # get all legal actions for pacman
        possible = state.getAllPossibleActions()
        # initalially assign actions to each chromosome
        # Population of size 8
        self.chromosomes = []
        for _ in range(0, 8):
            chromosome = []
            # Each chromosome is an action sequence of length 5
            for i in range(0, 5):
                chromosome.append(random.choice(possible))
            self.chromosomes.append(chromosome[:])
            # print chromosome

        # Keep highest ranked chromosomes
        self.ranked = []

        none_occurred = False
        while not none_occurred:
            ranked = []
            for chromosome in self.chromosomes:
                currState = state
                currScore = gameEvaluation(state, currState)
                for i in range(0, len(chromosome)):
                    # if the state is a win/lose state, break
                    if currState.isWin():
                        break
                    if currState.isLose():
                        break
                    # apply this action to curr state
                    currState = currState.generatePacmanSuccessor(chromosome[i])
                    if not currState:
                        none_occurred = True
                        break
                    else:
                        # update score
                        currScore = gameEvaluation(state, currState)
                ranked.append((chromosome[:], currScore))
            # sort score from high to low
            self.ranked = sorted(ranked, key = lambda pair: -pair[1])[:]
            # keep sorted chromosomes
            self.chromosomes = [pair[0] for pair in self.ranked][:]

            # population
            population = []
            while len(population) < len(self.chromosomes):
                chromosome_x = self.selection(self.chromosomes)
                chromosome_y = self.selection(self.chromosomes)
                if random.randint(1, 10) <= 7:
                    # 70% - crossover
                    chromosome_new = []
                    for i in range(0, len(chromosome_x)):
                        if random.randint(0, 1) == 0:
                            # 50% - choose x
                            chromosome_new.append(chromosome_x[i])
                        else:
                            chromosome_new.append(chromosome_y[i])
                    population.append(chromosome_new[:])
                else:
                    # 30% - keep both
                    population.append(chromosome_x[:])
                    population.append(chromosome_y[:])

            # Keep 8 chromosomes
            population = population[:len(self.chromosomes)]

            # mutated chromosomes
            for chromosome in population:
                if random.randint(1, 10) == 1:
                    # 10% - mutate the chromosome by random choice
                    rand_index = random.randint(0, 4)
                    chromosome[rand_index] = random.choice(possible)
            # new round
            self.chromosomes = population[:]
        # print self.ranked
        return self.ranked[0][0][0]

class MCTSAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        return

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # TODO: write MCTS Algorithm instead of returning Directions.STOP
        return Directions.STOP
