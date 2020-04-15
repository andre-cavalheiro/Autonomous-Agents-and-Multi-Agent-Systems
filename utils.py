from scipy.optimize import linprog
import numpy as np
import itertools

def calculateExpectedUtility(memoryFactor, utilityHistory):
    '''
    Calculate the expected utility for aspecific task taking into account its history of observations

    :param memoryFactor: int between one and zero
    :param utilityHistory:
    :return:
    '''
    if memoryFactor < 0 or memoryFactor > 1:
        raise Exception('Non valid memory factor {}'.format(memoryFactor))
    elif memoryFactor == 0:
        utilityValues = [v['val'] for v in utilityHistory]
        expectedUtility = sum(utilityValues) / len(utilityValues)
    else:
        denominator = sum([(u['step'])**memoryFactor for u in utilityHistory])
        formulaTerms = [u['val']*(((u['step'])**memoryFactor)/denominator)
                        for u in utilityHistory]
        expectedUtility = sum(formulaTerms)
    return expectedUtility


def singleUtilityToGo(expectedUtility, preparation, cyclesLeft, preparationSteps):
    '''
        Calculate utility-to-go for one task taking.

    :param expectedUtility: float
    :param preparation: int
    :param cyclesLeft: int
    :param preparationSteps: int
    :return:
    '''
    value = 0
    for _ in range(cyclesLeft):
        if preparation < preparationSteps:
            preparation += 1
        else:
            value += expectedUtility
    return value


def calculateUtilityToGo(tasks, currentStep, numCycles, restartCost):
    '''
    Calculate utility-to-go value for all tasks

    :param tasks: list of dictionaries
    :param currentStep: int
    :param numCycles: int
    :param restartCost: int
    :return:
    '''
    '''
    :param tasks: array of dictionaries of the following form:
    {
            'name': name,
            'timesExecuted': 0,
            'preparation': 0,
            'utility': float(utility),
            'utilityHistory': []
    }

    :return:
    '''
    cyclesLeft = numCycles-currentStep
    utilitiesToGo = [0 for _ in tasks]

    for it, task in enumerate(tasks):
        expectedUtility, preparation = task['utility'], task['preparation'],
        utilitiesToGo[it] = singleUtilityToGo(expectedUtility, preparation, cyclesLeft, restartCost)
    return utilitiesToGo


def chooseOptimalTaskDistribution(concurrencyCost, agents, tasks, infoPerTaskPerAgent, cyclesRemaining, restartCost):
    '''

    :param concurrencyCost: int
    :param agents: list
    :param tasks: list
    :param infoPerTaskPerAgent: dictionary of dictionaries with keys being the values in agents and tasks respectively
    :param cyclesRemaining:
    :param restartCost:
    :return:
    '''
    combinations = [p for p in itertools.product(tasks, repeat=len(agents))]
    highestGain, bestIndex = None, -1

    for combIndex, currentComb in enumerate(combinations):
        gain = 0
        for agtIndex, tskName in enumerate(currentComb):
            unique = len([val for val in currentComb if val == tskName]) == 1
            expectedUtility = infoPerTaskPerAgent[agents[agtIndex]][tskName]['utility']
            preparation = infoPerTaskPerAgent[agents[agtIndex]][tskName]['preparation']

            if not unique:
                expectedUtility -= concurrencyCost

            u2g = singleUtilityToGo(expectedUtility, preparation, cyclesRemaining, restartCost)
            gain += u2g

        if highestGain == None or gain > highestGain:
            highestGain = gain
            bestIndex = combIndex

    if highestGain == None:
        raise Exception('Impossible to find optimal task distribution')

    return combinations[bestIndex]


def chooseTaskPercentages(tasks):
    expectedUtilities, minObsUtilities = [], []
    for t in tasks:
        expectedUtilities.append(t['utility'])
        historyVals = [x['val'] for x in t['observedUtilityHistory']]
        if len(historyVals) > 0:
            minObsUtilities.append(min(historyVals))
        else:
            minObsUtilities.append(t['utility'])

    c = np.array(expectedUtilities) * -1
    A = [[1 for _ in expectedUtilities], np.array(minObsUtilities) * -1]    # Garantee sum to 1 and avoid minimal penalties
    b = [1, 0]
    result = linprog(c, A_ub=A, b_ub=b)
    percentages = result['x']
    return percentages


def assertActionsToTake(percentages):
    result = []
    for i, p in enumerate(percentages):
        if p>0.005:
            result.append({
                'index': i,
                'percentage': p
            })
    return result

