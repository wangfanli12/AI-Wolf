#!/usr/bin/env python
from __future__ import print_function, division
from os import stat

# This sample script connects to the AIWolf server, but
# does not do anything else. It will choose itself as the
# target for any actions requested by the server, (voting,
# attacking ,etc) forcing the server to choose a random target.

import aiwolfpy
import util
import aiwolfpy.contentbuilder as cb
from townPlayout import MCTS, gameState
from python_reporter import SampleAgent

myname = 'player1'

class agent1(SampleAgent):
    def __init__(self, agent_name):
        super().__init__(agent_name)

    def getName(self):
        return self.myname

    # new game (no return)
    def initialize(self, base_info, diff_data, game_setting):
        super().initialize(base_info, diff_data, game_setting)
        self.player_total = game_setting["playerNum"]
        self.player_score = [1]*self.player_total
        self.tree = MCTS()
        self.statusMap = base_info['statusMap']

    # new information (no return)
    def update(self, base_info, diff_data, request):
        super().update(base_info, diff_data, request)
        self.statusMap = base_info['statusMap']
        new_eval = self.evaluateWerewolf(base_info, diff_data)
        self.player_score = [self.player_score[i]*new_eval[i] for i in range (len(self.player_score))]
        state = gameState(self.getEvalDict(), 1, "town", {})
        for i in range(10):
            self.tree.do_rollout(state)

    def evaluateWerewolf(self, base_info, diff_data):
        eval = [1] * self.player_total

        # adds a point to the target for each vote
        # adds a point to the target for each mention of werewolf
        # subtract a point for coming out as a seer
        # subtract a point for being divined as a human
        for row in diff_data.itertuples():
            type = getattr(row,"type")
            text = getattr(row,"text")
            if (type == "vote"):
                voter = getattr(row,"idx")
                target = getattr(row,"agent")
                eval[target-1] += 1/sum(eval)
            elif (type == "talk"):
                source = getattr(row,"agent")
                target = util.getTarget(text)
                if "WEREWOLF" in text or "VOTE" in text:
                    eval[target-1] += 1/sum(eval)
                if (("DIVINED" in text and "HUMAN" in text) 
                    or ("COMINGOUT" in text and "SEER" in text)):
                    eval[target-1] -=  1/sum(eval)
        
        # change into percentage of total votes
        total = sum(eval)
        for i in range(len(eval)):
                eval[i] /= total
        return eval

    def getEvalDict(self):
        eval_dict = {}
        for key in self.statusMap.keys():
            if self.statusMap[key] == "DEAD":
                eval_dict[int(key)] = -1
            else:
                eval_dict[int(key)] = self.player_score[int(key)-1]
                
        return eval_dict

    # conversation actions: require a properly formatted
    # protocol string as the return.
    def talk(self):
        state = gameState(self.getEvalDict(), 1, "town", {})
        self.tree.do_rollout(state)
        choice = int(self.tree.choose(state).result['voted'])
        return "VOTE Agent[{:02d}]".format(choice)
    
    def vote(self):
        #super().logging.debug("# VOTE")
        state = gameState(self.getEvalDict(), 1, "town", {})
        self.tree.do_rollout(state)
        choice = int(self.tree.choose(state).result['voted'])
        return choice

agent = agent1(myname)

# run
if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
    # % python player1.py -h localhost -p 10000     