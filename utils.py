

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
        utilitiesToGo[it] = expectedUtility * (cyclesLeft-restart+preparation)
    return utilitiesToGo

def calculateExpectedUtility(utilityHistory):
    utilityValues = [v['val'] for v in utilityHistory]
    expectedUtility = sum(utilityValues)/len(utilityValues)
    return expectedUtility

def calculateUtilityWithMemoryFactor(memoryFactor, utilityHistory, step):
    if memoryFactor <= 0:
        raise Exception('Non valid memory factor {}'.format(memoryFactor))
    denominator = sum([(u['step'])**memoryFactor for u in utilityHistory])
    formulaTerms = [u['val']*(((u['step'])**memoryFactor)/denominator)
                    for u in utilityHistory]
    utility = sum(formulaTerms)
    return utility




