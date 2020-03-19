from utils import *

class singleAgent:

    def __init__(self, name, decisionType, restartCost, memoryFactor, numCyles):
        self.name = name
        self.decisionType = decisionType
        self.restartCost = restartCost
        self.memoryFactor = memoryFactor
        self.numCycles = numCyles

        self.tasks = []
        self.lastTaskIndex = None
        self.currentStep = 0
        self.gain = 0

    def newTask(self, task):
        self.tasks.append(task)

    def updateTaskUtility(self, newUtility):
        newUtility = float(newUtility)
        self.tasks[self.lastTaskIndex]['observedUtilityHistory'].append(newUtility)

        if self.memoryFactor == 0:
            expectedUtility = calculateExpectedUtility(self.tasks[self.lastTaskIndex]['observedUtilityHistory'])
            self.tasks[self.lastTaskIndex]['utility'] = expectedUtility
        else:
            newUtility = calculateUtilityWithMemoryFactor(self.memoryFactor, self.currentStep,
                                                          self.tasks[self.lastTaskIndex]['observedUtilityHistory'])
            self.tasks[self.lastTaskIndex]['utility'] = newUtility

        print('::[{}] Updated utility for {}, new value: {}'.format(self.name,
                                                                self.tasks[self.lastTaskIndex]['name'],
                                                                newUtility))

    def chooseAndExecuteAction(self):
        if self.decisionType == 'rationale':
            # Chooses task with higher known utility
            utilitiesToGo = utilityToGo(self.tasks, self.currentStep, self.numCycles,
                                        self.restartCost)
            actionIndex = utilitiesToGo.index(max(utilitiesToGo))
            self.actOnTask(actionIndex)
        elif self.decisionType == 'flexible':
            raise Exception('Not Implemented')
        elif self.decisionType == 'homogeneous-society':
            utilitiesToGo = utilityToGo(self.tasks, self.currentStep, self.numCycles,
                                        self.restartCost)
            actionIndex = utilitiesToGo.index(max(utilitiesToGo))
            self.actOnTask(actionIndex)
        elif self.decisionType == 'heterogeneous-society':
            utilitiesToGo = utilityToGo(self.tasks, self.currentStep, self.numCycles,
                                        self.restartCost)
            actionIndex = utilitiesToGo.index(max(utilitiesToGo))
            self.actOnTask(actionIndex)
        else:
            raise Exception('Unknown decision type {}'.format(self.decisionType))

    def actOnTask(self, index):
        if self.tasks[index]['preparation'] < self.restartCost:
            self.prepareTask(index)
        else:
            self.executeTask(index)

    def prepareTask(self, index):
        self.tasks[index]['preparation'] += 1
        print('>>[{}] Preparation step for task {}'.format(self.name, self.tasks[index]['name']))

    def executeTask(self, index):
        self.tasks[index]['executed'] = True
        self.lastTaskIndex = index
        print('->[{}] Executed task {}'.format(self.name, self.tasks[index]['name']))

    def incrementStep(self):
        self.currentStep += 1

    def addToGain(self, observedUtility):
        self.gain += float(observedUtility)

    def getGain(self):
        return self.gain

    def getFinalStatment(self, multiAgent):
        agentResults = '{}={{'.format(self.name) if multiAgent else '{'
        for i, ct in enumerate(self.tasks):
            agentResults += '{}={:.2f}'.format(ct['name'], ct['utility']) if ct['executed'] is True \
                else '{}=NA'.format(ct['name'])
            if i != len(self.tasks) - 1:
                agentResults += ','
        agentResults += '}'
        return agentResults
