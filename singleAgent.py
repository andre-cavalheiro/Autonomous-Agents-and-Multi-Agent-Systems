from utils import *

class singleAgent:

    def __init__(self, name, decisionType, restartCost, memoryFactor, numCyles, concurrencyPenalty, printController):
        self.name = name
        self.decisionType = decisionType
        self.restartCost = restartCost
        self.memoryFactor = memoryFactor
        self.numCycles = numCyles
        self.printController = printController
        self.concurrencyPenalty = concurrencyPenalty

        self.tasks = []
        self.lastTaskIndex = None
        self.currentStep = 0
        self.gain = 0

    def newTask(self, task):
        self.tasks.append(task)

    def updateTaskUtilities(self, newUtility, taskName=None):
        taskIdentifier = taskName if taskName is not None else self.lastTaskIndex

        newUtility = float(newUtility)
        self.tasks[taskIdentifier]['observedUtilityHistory'].append({
            'step': self.currentStep,
            'val': newUtility,
        })
        if self.printController:
            print('::[{}] New utility for {}, of value: {}'.format(self.name,
                                                                    self.tasks[taskIdentifier]['name'],
                                                                    newUtility))
        if self.memoryFactor == 0:
            expectedUtility = calculateExpectedUtility(self.tasks[taskIdentifier]['observedUtilityHistory'])
            self.tasks[taskIdentifier]['utility'] = expectedUtility
        else:
            expectedUtility = calculateUtilityWithMemoryFactor(self.memoryFactor,
                                                               self.tasks[taskIdentifier]['observedUtilityHistory'])
            self.tasks[taskIdentifier]['utility'] = expectedUtility

    def chooseAndExecuteAction(self):

        utilitiesToGo = utilityToGo(self.tasks, self.currentStep, self.numCycles,
                                    self.restartCost)
        if self.printController:
            print('======================================')
            print('======================================')
            print('Iteration: {}'.format(self.currentStep))
            currentExpectedUtilitiesSTR = ['{}({:.2f}) ||'.format(i['name'], i['utility']) for i in self.tasks]
            print('U    {}   '.format(currentExpectedUtilitiesSTR))
            preparationStepsSTR = ['{}({:.2f}) ||'.format(i['name'], i['preparation']) for i in self.tasks]
            print('P    {}   '.format(preparationStepsSTR))
            utilitiesToGoSTR = ['{}({:.2f}) ||'.format(self.tasks[i]['name'], v) for i, v in enumerate(utilitiesToGo)]
            print('U2G    {}   '.format(utilitiesToGoSTR))

        if self.decisionType == 'rationale' or \
                self.decisionType == 'homogeneous-society' or \
                self.decisionType == 'heterogeneous-society':

            maxUtilityValue = max(utilitiesToGo)
            if maxUtilityValue > 0:
                actionIndex = utilitiesToGo.index(maxUtilityValue)
                self.actOnTask(actionIndex)
        elif 'flexible' in self.decisionType:
            percentagesPerTask = chooseTaskPercentages(self.tasks)
            actions = assertActionsToTake(percentagesPerTask)

            if len(actions) > 1:
                str = '{'
                for a in actions:
                    self.actOnTask(a['index'], a['percentage'])
                    str += '{}={:.2f},'.format(self.tasks[a['index']]['name'], a['percentage'])
                str = str[:-1]  # Remove last colon
                str += '}'
                print(str)
            else:
                self.actOnTask(actions[0]['index'], actions[0]['percentage'])
        else:
            raise Exception('Unknown decision type {}'.format(self.decisionType))

    def actOnTask(self, index, percentage=1):
        # Set all of the preparation steps that are NOT of the current task to zero
        for i in range(len(self.tasks)):
            if i != index:
                self.tasks[i]['preparation'] = 0

        if self.tasks[index]['preparation'] < self.restartCost:
            self.prepareTask(index)
        else:
            self.executeTask(index, percentage)

    def prepareTask(self, index):
        self.tasks[index]['preparation'] += 1
        if self.printController:
            print('>>[{}] Preparation step for task {}'.format(self.name, self.tasks[index]['name']))

    def executeTask(self, index, percentage=1):
        self.tasks[index]['executed'] = True
        self.tasks[index]['executePercentage'] = percentage
        self.lastTaskIndex = index
        if self.printController:
            print('->[{}] Executed task {} w/ percentage {}'.format(self.name, self.tasks[index]['name'], percentage))

    def incrementStep(self):
        self.currentStep += 1

    def addToGain(self, observedUtilities):
        if isinstance(observedUtilities, dict):
            for k, v in observedUtilities.items():
                index = self.getTaskIndexByName(k)
                self.gain += self.tasks[index]['executePercentage']*v
        else:
            self.gain += float(observedUtilities)

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

    def getTaskIndexByName(self, name):
        for i, t in enumerate(self.tasks):
            if t['name'] == name:
                return i

    def getTasks(self):
        currentUtils = {
            t['name']: {
                'utility': t['utility'],
                'preparation': t['preparation']
                }
            for t in self.tasks
        }
        return currentUtils

    def getLastTaskName(self):
        return self.tasks[self.lastTaskIndex]['name']
