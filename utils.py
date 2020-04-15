import math
from scipy.optimize import linprog
import numpy as np
import math
import itertools


def utilityToGo(tasks, currentStep, numCycles, restart):
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
        utilitiesToGo[it] = singleUtilityToGo(expectedUtility, preparation, cyclesLeft, restart)
    return utilitiesToGo


def singleUtilityToGo(expectedUtility, preparation, cyclesLeft, restartCost):
    value = 0
    for _ in range(cyclesLeft):
        if preparation < restartCost:
            preparation += 1
        else:
            value += expectedUtility
    return value


def calculateExpectedUtility(utilityHistory):
    utilityValues = [v['val'] for v in utilityHistory]
    expectedUtility = sum(utilityValues)/len(utilityValues)
    return expectedUtility


def calculateUtilityWithMemoryFactor(memoryFactor, utilityHistory):
    if memoryFactor <= 0:
        raise Exception('Non valid memory factor {}'.format(memoryFactor))
    denominator = sum([(u['step'])**memoryFactor for u in utilityHistory])
    formulaTerms = [u['val']*(((u['step'])**memoryFactor)/denominator)
                    for u in utilityHistory]
    utility = sum(formulaTerms)
    return utility


def chooseOptimalTaskDistribution(cost, agents, tasks, infoPerTaskPerAgent, cyclesRemaining, restartCost):
    combinations = [p for p in itertools.product(tasks, repeat=len(agents))]
    highestGain, bestIndex = None, -1

    for combIndex, currentComb in enumerate(combinations):
        gain = 0
        for agtIndex, tskName in enumerate(currentComb):
            unique = len([val for val in currentComb if val == tskName]) == 1
            expectedUtility = infoPerTaskPerAgent[agents[agtIndex]][tskName]['utility']
            preparation = infoPerTaskPerAgent[agents[agtIndex]][tskName]['preparation']

            if not unique:
                expectedUtility -= cost

            u2g = singleUtilityToGo(expectedUtility, preparation, cyclesRemaining, restartCost)
            gain += u2g

        if highestGain == None or gain > highestGain:
            highestGain = gain
            bestIndex = combIndex

    if bestIndex == -1:
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
    percentages = [i * 1000 + 1 for i in percentages]
    percentages = round_series_retain_integer_sum(percentages)
    percentages = [i / 1000 for i in percentages]
    result = []
    for i, p in enumerate(percentages):
        if p>0.005:
            result.append({
                'index': i,
                'percentage': p
            })
    return result


def round_series_retain_integer_sum(xs):
    N = sum(xs)
    Rs = [math.trunc(x) for x in xs]
    K = int(N - sum(Rs))
    assert (K == round(K))
    fs = [x - round(x) for x in xs]
    indices = [i for order, (e, i) in enumerate(reversed(sorted((e, i) for i, e in enumerate(fs)))) if order < K]
    ys = [R + 1 if i in indices else R for i, R in enumerate(Rs)]
    return ys


