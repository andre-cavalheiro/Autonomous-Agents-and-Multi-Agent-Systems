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
            expectedUtility = calculateUtilityWithMemoryFactor(self.memoryFactor,
                                                               self.tasks[self.lastTaskIndex]['observedUtilityHistory'])
            self.tasks[self.lastTaskIndex]['utility'] = expectedUtility

        '''print('::[{}] Updated utility for {}, new value: {}'.format(self.name,
                                                                self.tasks[self.lastTaskIndex]['name'],
                                                                expectedUtility))'''

    def chooseAndExecuteAction(self):
        if self.decisionType == 'rationale' or \
                self.decisionType == 'homogeneous-society' or \
                self.decisionType == 'heterogeneous-society':

            print('Iteration: {}'.format(self.currentStep))
            currentExpectedUtilities = ['{}({:.2f}) ||'.format(i['name'], i['utility']) for i in self.tasks]
            print('    {}   '.format(currentExpectedUtilities))

            utilitiesToGo = utilityToGo(self.tasks, self.currentStep, self.numCycles,
                                        self.restartCost)
            maxUtilityValue = max(utilitiesToGo)
            if maxUtilityValue > 0:
                actionIndex = utilitiesToGo.index(maxUtilityValue)
                self.actOnTask(actionIndex)
        elif self.decisionType == 'flexible':
            raise Exception('Not Implemented')
        else:
            raise Exception('Unknown decision type {}'.format(self.decisionType))

    def actOnTask(self, index):
        if index != self.lastTaskIndex and self.lastTaskIndex is not None:
            # If I'm gonna change tasks, I loose all the preparation I had for the previous one
            self.tasks[self.lastTaskIndex]['preparation'] = 0

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
