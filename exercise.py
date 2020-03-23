import sys
import traceback

from utils import *
from singleAgent import singleAgent

#########################
### A: AGENT BEHAVIOR ###
#########################

class Agent:
    agents = {}
    configuration = {}
    multiAgent = False

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
            splitInput = input.split(' ')
            agentName = splitInput[0]
            newUtility = splitInput[1].split('=')[1]
            if 'homogeneous' in self.configuration['decision']:
                for a in self.agents.values():
                    a.updateTaskUtility(newUtility)
            else:
                self.agents[agentName].updateTaskUtility(newUtility)

            self.agents[agentName].addToGain(newUtility)

        else:
            raise Exception('Unknown perception: {}'.format(input))

    def decide_act(self):
        for k, a in self.agents.items():
            a.chooseAndExecuteAction()
            a.incrementStep()

    def recharge(self):
        statment = 'state={' if self.multiAgent else 'state='
        gain = 0
        for k, a in self.agents.items():
            agentResults = a.getFinalStatment(self.multiAgent)
            statment += agentResults
            gain += a.getGain()
            if self.multiAgent:
                statment += ','
        if self.multiAgent:
            statment += '}'
        statment += ' gain={:.2f}'.format(gain)
        return statment

    def createTask(self, name, utility):
        task = {
                'name': name,
                'executed': False,
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
                               self.configuration['cycle'])
        return newAgent

    def printParams(self):
        print('== Current Configuration ==')
        for k, v in self.configuration.items():
            print('> {}: {}'.format(k, v))
        print('============================')


#####################
### B: MAIN UTILS ###
#####################

#fileName = 'statement\T03_input.txt'
fileName = 'cases\T13_input.txt'
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
