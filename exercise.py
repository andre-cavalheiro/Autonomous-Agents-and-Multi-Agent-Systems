import sys
import traceback

from utils import *

#########################
### A: AGENT BEHAVIOR ###
#########################

class Agent:
    currentStep = 0
    gain = 0
    tasks = []
    lastTaskIndex = None
    configuration = {}

    def __init__(self, options):
        ignoreTerms = ['', '\n']
        integerParameters = ['cycle', 'restart']
        floatParameters = ['memory-factor']
        for i in range(len(options)):
            if options[i] in ignoreTerms:
                break
            paramInfo = options[i].split('=')
            paramName = paramInfo[0]
            paramValue = paramInfo[1]
            paramValue = paramValue if paramName not in integerParameters else int(paramInfo[1])
            paramValue = paramValue if paramName not in floatParameters else float(paramInfo[1])
            self.configuration[paramName] = paramValue

        if 'restart' not in self.configuration.keys():
            self.configuration['restart'] = 0
        if 'memory-factor' not in self.configuration.keys():
            self.configuration['memory-factor'] = 0
        if 'society' in self.configuration['decision']:
            assert('agents' in self.configuration.keys())
            agentsAsString = self.configuration['agents']
            agents = agentsAsString.replace('{', '').replace('}', '').split(',')
            self.configuration['agents'] = [self.createAgent(n) for n in agents]

        self.printParams()

    def perceive(self, input):
        if input.startswith('T'):
            # New task
            splitInput = input.split(' ')
            taskName, expectedUtility = splitInput[0], splitInput[1].split('=')[1]
            self.tasks.append(self.createTask(taskName, expectedUtility))
            print('- Aware of task {}'.format(taskName))
        elif input.startswith('A'):
            # Update utility
            splitInput = input.split(' ')
            newUtility = splitInput[1].split('=')[1]
            if 'society' in self.configuration['decision']:
                raise Exception('Not implemented')
            else:
                self.updateUtility(newUtility)
        else:
            raise Exception('Unknown perception: {}'.format(input))

    def decide_act(self):
        if self.configuration['decision'] == 'rationale':
            # Chooses task with higher known utility
            utilitiesToGo = utilityToGo(self.tasks, self.currentStep, self.configuration['cycle'],
                                        self.configuration['restart'])
            actionIndex = utilitiesToGo.index(max(utilitiesToGo))
            self.actOnTask(actionIndex)
        elif self.configuration['decision'] == 'flexible':
            raise Exception('Not Implemented')
        elif self.configuration['decision'] == 'homogeneous-society':
            raise Exception('Not Implemented')
        elif self.configuration['decision'] == 'heterogeneous-society':
            raise Exception('Not Implemented')
        else:
            raise Exception('Unknown agent type {}'.format(self.decisionType))
        self.currentStep +=1

    def recharge(self):
        if 'society' in self.configuration['decision']:
            raise Exception('Not implemented')
        else:
            results = 'state={'
            gain = 0
            for i, ct in enumerate(self.tasks):
                gain += ct['utility']*ct['timesExecuted']
                results += '{}={:.2f}'.format(ct['name'], ct['utility']) if ct['timesExecuted'] != 0 \
                    else '{}=NA'.format(ct['name'])
                if i != len(self.tasks)-1:
                    results += ','
            results += '}} gain={:.2f}'.format(self.gain)
            return results

    def actOnTask(self, index):
        if self.tasks[index]['preparation'] < self.configuration['restart']:
            self.prepareTask(index)
        else:
            self.executeTask(index)

    def prepareTask(self, index):
        self.tasks[index]['preparation'] += 1
        print('>> Preparation step for task {}'.format(self.tasks[index]['name']))

    def executeTask(self, index):
        self.tasks[index]['timesExecuted'] += 1
        self.lastTaskIndex = index
        print('-> Executed task {}'.format(self.tasks[index]['name']))

    def createTask(self, name, utility):
        task = {
                'name': name,
                'timesExecuted': 0,
                'preparation': 0,
                'utility': float(utility),
                'observedUtilityHistory': [],
            }
        return task

    def createAgent(self, name):
        agent = {
                'name': name,
            }
        return agent

    def updateUtility(self, utility):
        self.tasks[self.lastTaskIndex]['observedUtilityHistory'].append(float(utility))
        self.gain += float(utility)
        if self.configuration['memory-factor'] == 0:
            newUtility = utility
            self.tasks[self.lastTaskIndex]['utility'] = float(newUtility)
        else:
            newUtility = calculateUtilityWithMemoryFactor(self.configuration['memory-factor'], self.currentStep,
                                                          self.tasks[self.lastTaskIndex]['observedUtilityHistory'])
            self.tasks[self.lastTaskIndex]['utility'] = float(newUtility)

        print(':: Updated utility for {}, new value: {}'.format(self.tasks[self.lastTaskIndex]['name'],
                                                                newUtility))

    def printParams(self):
        print('== Current Configuration ==')
        for k, v in self.configuration.items():
            print('> {}: {}'.format(k, v))
        print('============================')

#####################
### B: MAIN UTILS ###
#####################

fileName = 'statement\T01_input.txt'
f = open(fileName, 'r')
line = f.readline()

# line = sys.stdin.readline()
agent = Agent(line.split(' '))
try:
    # for line in sys.stdin:
    for line in f:
        if line.startswith("end"): break
        elif line.startswith("TIK"): agent.decide_act()
        else: agent.perceive(line)
    sys.stdout.write(agent.recharge()+'\n');
except:
    print(traceback.format_exc())
