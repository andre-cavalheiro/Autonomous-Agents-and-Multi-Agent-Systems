import sys
import traceback

#########################
### A: AGENT BEHAVIOR ###
#########################

class Agent:
    tasks = []
    lastTaskIndex = None
    configuration = {}

    def __init__(self, options):
        ignoreTerms = ['', '\n']
        numberParameters = ['cycle', 'restart']
        for i in range(len(options)):
            if options[i] in ignoreTerms:
                break
            paramInfo = options[i].split('=')
            paramName = paramInfo[0]
            paramValue = paramInfo[1] if paramName not in numberParameters else int(paramInfo[1])
            self.configuration[paramName] = paramValue

        if 'restart' not in self.configuration.keys():
            self.configuration['restart'] = 0

        if 'society' in self.configuration['decision'].keys():
            assert('agents' in self.configuration.keys())
            agentsAsString = self.configuration['agents']
            agents = agentsAsString.replace('{', '').replace('}', '').split(',')
            self.configuration['agents'] = [self.createAgents(n) for n in agents]

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
            realUtility = splitInput[1].split('=')[1]
            if 'society' in self.configuration['decision']:
                raise Exception('Not implemented')
            else:
                self.tasks[self.lastTaskIndex]['utility'] = float(realUtility)
                print(':: Updated utility for {}'.format(self.tasks[self.lastTaskIndex]['name']))
        else:
            raise Exception('Unknown perception: {}'.format(input))

    def decide_act(self):
        if self.configuration['decision'] == 'rationale':
            # Chooses task with higher known utility
            maxExpectUtilityIndex = max(range(len(self.tasks)), key=lambda
                index: self.tasks[index]['utility'])

            if self.tasks[maxExpectUtilityIndex]['preparation'] < self.configuration['restart']:
                self.tasks[maxExpectUtilityIndex]['preparation'] += 1
                print('>> Preparation step for task {}'.format(self.tasks[maxExpectUtilityIndex]['name']))
                return
            else:
                self.tasks[maxExpectUtilityIndex]['timesExecuted'] += 1
                self.lastTaskIndex = maxExpectUtilityIndex
                print('-> Executed task {}'.format(self.tasks[maxExpectUtilityIndex]['name']))

        elif self.configuration['decision'] == 'flexible':
            raise Exception('Not Implemented')
        elif self.configuration['decision'] == 'homogeneous-society':
            raise Exception('Not Implemented')
        elif self.configuration['decision'] == 'heterogeneous-society':
            raise Exception('Not Implemented')

        else:
            raise Exception('Unknown agent type {}'.format(self.decisionType))

    def recharge(self):
        if 'society' in self.configuration['decision']:
            raise Exception('Not implemented')
        else:
            results = 'state={'
            gain = 0
            for i, ct in enumerate(self.tasks):
                gain += ct['utility']*ct['timesExecuted']
                results += '{}={:.2f}'.format(ct['name'], ct['utility']) if ct['timesExecuted'] !=0 \
                    else '{}=NA'.format(ct['name'])
                if i != len(self.tasks)-1:
                    results += ','
            results += '}} gain={:.2f}'.format(gain)
            return results

    def printParams(self):
        print('== Current Configuration ==')
        for k, v in self.configuration.items():
            print('> {}: {}'.format(k, v))
        print('============================')

    def createTask(self, name, utility):
        task = {
                'name': name,
                'timesExecuted': 0,
                'preparation': 0,
                'utility': float(utility),
            }
        return task

    def createAgents(self, name):
        agent = {
                'name': name,
                'taskHistory': []
            }
        return agent


#####################
### B: MAIN UTILS ###
#####################

fileName = 'statement\T02_input.txt'
f = open(fileName, 'r')
line = f.readline()

# line = sys.stdin.readline()
agent = Agent(line.split(' '))
try:
    #for line in sys.stdin:
    for line in f:
        if line.startswith("end"): break
        elif line.startswith("TIK"): agent.decide_act()
        else: agent.perceive(line)
    sys.stdout.write(agent.recharge()+'\n');
except:
    print(traceback.format_exc())
