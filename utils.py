

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
        utilitiesToGo[it] = expectedUtility * (cyclesLeft-restart)
    return utilitiesToGo

def calculateExpectedUtility(utilityHistory):
    expectedUtility = sum(utilityHistory)/len(utilityHistory)
    return expectedUtility

def calculateUtilityWithMemoryFactor(memoryFactor, utilityHistory):
    if memoryFactor <= 0:
        raise Exception('Non valid memory factor {}'.format(memoryFactor))
    denominator = sum([(i+1)**memoryFactor for i in range(len(utilityHistory))])
    formulaTerms = [u*(((i+1)**memoryFactor)/denominator) for i, u in enumerate(utilityHistory)]
    utility = sum(formulaTerms)
    return utility




