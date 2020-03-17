

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
        utility, preparation = task['utility'], task['preparation'],
        for c in range(cyclesLeft):
            if preparation < restart:
                utilitiesToGo[it] += 0
                preparation += 1
            else:
                utilitiesToGo[it] += utility
    return utilitiesToGo


def calculateUtilityWithMemoryFactor(memoryFactor, currentStep, utilityHistory):
    if memoryFactor <= 0:
        raise Exception('Non valid memory factor {}'.format(memoryFactor))
    denominator = sum([(i+1)**memoryFactor for i in range(currentStep)])
    formulaTerms = [u*(((i+1)**memoryFactor)/denominator) for i, u in enumerate(utilityHistory)]
    utility = sum(formulaTerms)
    return utility
