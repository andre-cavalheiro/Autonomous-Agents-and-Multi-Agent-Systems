import sys
import traceback
import math
from utils import *
from singleAgent import singleAgent

#########################
### A: AGENT BEHAVIOR ###
#########################

class Agent:
    agents = {}
    configuration = {}
    multiAgent = False

    def __init__(self, options, printController):
        self.printController = printController
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

        if self.printController:
            self.printParams()
        self.initAgents()

    def initAgents(self):
        if 'society' in self.configuration['decision']:
            self.multiAgent = True
            assert('agents' in self.configuration.keys())
            agentsAsString = self.configuration['agents']
            agents = agentsAsString.replace('{', '').replace('}', '').replace('[', '').replace(']', '').split(',')
            self.agents = {n: self.createAgent(n) for n in agents}
        else:
            self.agents = {'A': self.createAgent('A')}

    def perceive(self, input):
        if input.startswith('T'):
            # New task
            splitInput = input.split(' ')
            taskName, expectedUtility = splitInput[0], splitInput[1].split('=')[1]
            for k, a in self.agents.items():
                a.newTask(self.createTask(taskName, expectedUtility))

        elif input.startswith('A'):
            # Update utility
            if 'flexible' in self.configuration['decision']:
                # A u = {T1 = 3, T2 = 2}
                splitInput = input.split(' ')
                agentName = splitInput[0]
                remainingInfo = splitInput[1].split('u=')

                if remainingInfo[1].startswith('{'):
                    remainingInfo = remainingInfo[1].replace('\n', '').replace('{', '').replace('}', '').split(',')
                    utilityPerTask = {}
                    for task in remainingInfo:
                        taskInfo = task.split('=')
                        utilityPerTask[taskInfo[0]] = float(taskInfo[1])
                    for k, v in utilityPerTask.items():
                        taskIndex = self.agents[agentName].getTaskIndexByName(k)
                        self.agents[agentName].updateTaskUtilities(v, taskIndex)
                    self.agents[agentName].addToGain(utilityPerTask)
                else:
                    newUtility = remainingInfo[1]
                    self.agents[agentName].updateTaskUtilities(newUtility)
                    self.agents[agentName].addToGain(newUtility)

            else:
                splitInput = input.split(' ')
                agentName = splitInput[0]
                newUtility = splitInput[1].split('=')[1]
                if 'homogeneous' in self.configuration['decision']:
                    for a in self.agents.values():
                        a.updateTaskUtilities(newUtility)
                else:
                    self.agents[agentName].updateTaskUtilities(newUtility)
                self.agents[agentName].addToGain(newUtility)

        else:
            raise Exception('Unknown perception: {}'.format(input))

    def decide_act(self):
        executedTasks, executingAgents = [None for _ in range(len(self.agents))], [None for _ in range(len(self.agents))]
        for k, a in enumerate(self.agents.items()):
            taskName = a.chooseAndExecuteAction()
            executingAgents.append(k)
            executedTasks.append(taskName)
            a.incrementStep()

    def recharge(self):
        statment = 'state={' if self.multiAgent else 'state='
        gain = 0
        for i, (k, a) in enumerate(self.agents.items()):
            agentResults = a.getFinalStatment(self.multiAgent)
            statment += agentResults
            gain += a.getGain()
            if self.multiAgent and i != len(self.agents)-1:
                statment += ','
        if self.multiAgent:
            statment += '}'

        statment += ' gain={:.2f}'.format(gain)
        return statment

    def createTask(self, name, utility):
        task = {
                'name': name,
                'executed': False,
                'executePercentage': 0,
                'preparation': 0,
                'utility': float(utility),
                'observedUtilityHistory': [],
            }
        return task

    def createAgent(self, name):
        newAgent = singleAgent(name,
                               self.configuration['decision'],
                               self.configuration['restart'],
                               self.configuration['memory-factor'],
                               self.configuration['cycle'],
                               self.configuration['concurrency-penalty'],
                               self.printController)
        return newAgent

    def printParams(self):
        print('== Current Configuration ==')
        for k, v in self.configuration.items():
            print('> {}: {}'.format(k, v))
        print('============================')


#####################
### B: MAIN UTILS ###
#####################
# To run in the traditional way: 'cat 'cases/T00_input.txt' | py .\exercise.py'
printController = False

# fixme - mooshak 12!!!

# fileName = 'statement\T04_input.txt'
# fileName = 'cases\T08_input.txt'
fileName = 'mooshakCases\T18_input.txt'
f = open(fileName, 'r')
line = f.readline()

#line = sys.stdin.readline()
agent = Agent(line.split(' '), printController)
try:
    #for line in sys.stdin:
    for line in f:
        if line.startswith("end"): break
        elif line.startswith("TIK"): agent.decide_act()
        else: agent.perceive(line)
    sys.stdout.write(agent.recharge()+'\n')
except:
    print(traceback.format_exc())
