'''
Created on Apr 13, 2021

@author: starw
'''

import random
from abc import ABC, abstractmethod
from collections import defaultdict
import math
from itertools import combinations
from numpy.core.numeric import roll

#handle negative number

class gameState:
    def __init__(self, elva_dict, werewolfNum, faction, result_dict):
        self.elva_dict = elva_dict
        dict(sorted(self.elva_dict.items(), key=lambda item:item[1], reverse=True))
        self.assumption = {}
        self.result = result_dict
        self.werewolf = werewolfNum
        self.faction = faction
        assumption = {}
        self.werewolfWin = False
        self.children = {}
        #print(self.elva_dict)
        #Assume a role based on the probability from evaluation        
        for i in self.elva_dict:
            if self.elva_dict.get(i) < 0:
                continue
            randomNum = random.random()
            if self.elva_dict.get(i) >= randomNum:
                if werewolfNum <= 0:
                    assumption[i] = False
                else:
                    assumption[i] = True
                    werewolfNum -= 1
            else:
                assumption[i] = False
        self.assumption = assumption
        while werewolfNum > 0:
            #print(self.assumption)
            #print("num of werewolf left: ", werewolfNum)
            for i in assumption:
                if assumption[i] == False and werewolfNum > 0:
                    assumption[i] = True 
                    werewolfNum -= 1
            if self.isTerminal() == True:
                break
                    
        self.assumption = assumption
    
    #if the rest of the assumed role belongs to only one faction, return true
    def isTerminal(self):
        condition = False
        self.werewolfWin = False
        #print(self.assumption)
        if all(self.assumption[i] == True for i in self.assumption):
            condition = True
            self.werewolfWin = True
        elif all(self.assumption[i] == False for i in self.assumption):
            condition = True
            self.werewolfWin = False
        if len(self.assumption) == 2:
            condition = True 
            self.werewolfWin = True
        return condition
    
    def toString(self):
        return self.assumption
    
    
    def nextState(self):
        if self.isTerminal():
            print("Jesus Christ")
            return 
        #vote out the most likely werewolf
        l = list(self.assumption.items())
        random.shuffle(l)
        self.assumption = dict(l)
        for i in self.assumption:
            newWolfNum = self.werewolf
            result = {"voted":i}
            newElva_dict = self.elva_dict.copy()
            newAssumption = self.assumption.copy()
            newAssumption.pop(i)
            newElva_dict[i] = -1
            if self.assumption[i] == True:
                newWolfNum -= 1
            #print("voted", newAssumption)
            break
        dict_assumption = self.nightKill(newElva_dict, newAssumption)
        print("new game state, 1: ", dict_assumption[1])
        return gameState(dict_assumption[0], newWolfNum, self.faction, result)
    
    #kill a random person at night
    def nightKill(self, newElvaDict, newAssumption):
        kill = False
        killIndex = newAssumption.copy()
        l = list(killIndex.items())
        random.shuffle(l)
        killIndex = dict(l)
        for i in killIndex:
            if newAssumption.get(i) == False:
                newAssumption.pop(i)
                newElvaDict[i] = -1
                #print("killed", newAssumption)
                break
        return newElvaDict, newAssumption
        
        
    def find_random_child(self):
        return random.choice(self.find_children_vote())

    # def findChild(self):
    #     dead_combination = combinations(self.elva_dict.keys(), 2) # returns a combination of 2 to be dead. ex. [(1,2),(1,3),(2,3)]
        
    #     for dead_tuple in dead_combination:
    #         child_elva = []
    #         for key in self.elva_dict.keys():
    #             if key not in dead_tuple:
    #                 child_elva[key] = self.elva_dict[key]
    #         self.children.append(gameState(self.elva_dict, self.werewolf, self.faction))

    def find_children_vote(self):
        if self.isTerminal() == True:
            #print("OMG")
            return {}
        newSet = set()
        for i in self.assumption:
            newWolfNum = self.werewolf
            newElva_dict = self.elva_dict.copy()
            newAssumption = self.assumption.copy()
            newAssumption.pop(i)
            if self.assumption[i] == True:
                newWolfNum -= 1
            newElva_dict[i] = -1
            voted = {'voted':i}
            #print("old assumption: ", newAssumption, newWolfNum)
            dict_assumption = self.nightKill(newElva_dict, newAssumption)
            #self.children[i] = gameState(dict_assumption[0], self.werewolf, self.faction, voted)
            #print("new game state, 2: ", dict_assumption[0])
            newSet.add(gameState(dict_assumption[0], newWolfNum, self.faction, voted))
        #for i in newSet:
            #print("In the new Set: ", i.toString())
        return newSet
    
    def getResult(self):
        return self.result

    def reward(self):
        if self.faction == "werewolf":
            if self.werewolfWin:
                return 1
            else:
                return 0
        else:
            print("returning reward: ", self.assumption)
            if self.werewolfWin:
                #print("returned 0")
                return 0
            else:
                #print("returned 1")
                return 1

    def __hash__(self):
        return hash(str(self))

    """
    def __eq__(self, gameState2):
        "Nodes must be comparable"
        return self.elva_dict == gameState2.elva_dict
        """

    """
    def __assign(self, elva_dict):
        assumed_dict = elva_dict.copy()
        for i in assumed_dict:
    """

"""
class simulation():
    win = False
    state = gameState()
    while(state.isTerminal() != True):
        action = state.getAction()
        state.getNextState(action)
        
    return state.getWin()
"""

class MCTS:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, exploration_weight=math.sqrt(2)):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = dict()  # children of each node
        self.exploration_weight = exploration_weight

    def choose(self, node):
        "Choose the best successor of node. (Choose a move in the game)"
        if node.isTerminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if node not in self.children:
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves
            return self.Q[n] / self.N[n]  # average reward

        #print("The reward is: ", self.N)
        return max(self.children[node], key=score)

    def do_rollout(self, node):
        "Make the tree one layer better. (Train for one iteration.)"
        #print("Roll out starts! : ",node.toString())
        path = self._select(node)
        #print("structure of node: ", path)
        leaf = path[-1]
        #print("the leaf is selected: ", leaf.toString())
        self._expand(leaf)
        reward = self._simulate(leaf)
        #print("leaf reward: ", reward)
        self._backpropagate(path, reward)

    def _select(self, node):
        "Find an unexplored descendent of `node`"
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            #for i in self.children[node]:
                #print("here's a child: ", i.toString())
            unexplored = self.children[node] - self.children.keys() # UPDATED TO WORK WITH DICT
            #print("unexplored list: ", unexplored)
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                #print("found unexplored")
                return path
            #print("the deep dark: ")
            node = self._uct_select(node)  # descend a layer deeper

    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node in self.children:
            return  # already expanded
        self.children[node] = node.find_children_vote()
        #for i in self.children[node]:
            #print("expanded: ", i.toString())

    def _simulate(self, node):
        "Returns the reward for a random simulation (to completion) of `node`"
        #invert_reward = True
        while True:
            if node.isTerminal():
                reward = node.reward()
                #return 1 - reward if invert_reward else reward
                return reward
            node = node.nextState()
            #invert_reward = not invert_reward

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward
            #reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )

        return max(self.children[node], key=uct)
    
    # def __str__(self, level=0):
    #     ret = "\t"*level+repr(self.Q)+"\n"
    #     for child in self.children:
    #         ret += child.__str__(level+1)
    #     return ret

    # def __repr__(self):
    #     return '<tree representation>'
    
class simulation:
    def __init__(self, testDict, werewolfNum, faction, tree, rollOutTimes, testTimes = 10):
        self.testDict = testDict
        self.tree = tree
        self.rollOutTimes = rollOutTimes
        self.wereWolfNum = werewolfNum
        self.faction = faction
        self.testTimes = 50
        
    def bestAction(self):
        choice = defaultdict(int)
        for l in range(self.testTimes):
            newState = gameState(self.testDict, self.wereWolfNum, self.faction, {})
            for i in range(self.rollOutTimes):
                #print(newState.toString())
                self.tree.do_rollout(newState)
            choice[self.tree.choose(newState).getResult().get('voted')] += 1
        return choice
            
        


if __name__ == '__main__':
    testDict = {1:0.7, 2:0.21, 3:0.41, 4:0.5, 5:0.3}
    #test = gameState(testDict, 2, "town", {})

    
    #print(test.isTerminal())
    #print(test.reward())
    #test.nextState()
    #print(test.isTerminal())
    #print(test.reward())
    tree = MCTS()
    """
    tree = MCTS()
    for i in range(100):
        tree.do_rollout(test)
    choice = tree.choose(test)
    print(test.toString())
    print(choice.toString())
    print(choice.getResult())
    """
    newSimulation = simulation(testDict, 2, "town", tree, 50)
    print(newSimulation.bestAction())


    