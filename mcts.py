'''
@Author: Hanxun Zhong
@Date: 2020-07-20 19:19:35
@LastEditTime: 2020-07-27 16:17:02
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /Gobang/mcts.py
'''
import copy
import math
import logging
import numpy as np
from operator import itemgetter
def policy_value_fn(board):
    """a function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state"""
    # return uniform probabilities and 0 score for pure MCTS
    action_probs = np.ones(len(board.availables))/len(board.availables)
    return zip(board.availables, action_probs)
    
def rollout_policy_fn(board):
    """a coarse, fast version of policy_fn used in the rollout phase."""
    # rollout randomly
    action_probs = np.random.rand(len(board.availables))
    return zip(board.availables, action_probs)


class Node():
    def __init__(self, parent):
        self.parent = parent
        self.child = {}
        self.visits = 0
        self.value = 0.0
    
    def expand(self, act_prods):
        for action, prods in act_prods:
            if action not in self.child:
                self.child[action] = Node(self)
    
    def select(self):
        return max(self.child.items(), key=lambda act_nodes: act_nodes[1].get_value())

    def update(self, leaf_value):
        self.value += 1.0*(leaf_value - self.value) / (self.visits + 1)
        self.visits += 1

    def update_recursive(self, value):
        if self.parent:
            self.parent.update_recursive(value)
        self.update(value)

    def get_value(self, is_expolration=True):
        if is_expolration:
            C = 1 / math.sqrt(2)
        else:
            C = 0
        # UCB = quality / times + C * sqrt(2 * ln(total_times) / times)
        left = self.value / (self.visits + 1)
        right = 2 * math.log(self.parent.visits) / (self.visits + 1)
        ucb = left + C * math.sqrt(right)
        return ucb

    def is_leaf(self):
        return not self.child

    def is_root(self):
        return not self.parent

class Mcts():
    def __init__(self, logger, step=100, policy_fc=policy_value_fn):
        self.root = Node(None)
        self.steps = step
        self.policy = policy_fc
        self.logger = logger

    def get_move(self, state):
        for n in range(self.steps):
            state_copy = copy.deepcopy(state)
            self.play_out(state_copy)
        return max(self.root.child.items(), key=lambda act_node: act_node[1].visits)[0]

    def play_out(self, state):
        node = self.root
        while not node.is_leaf():
            action, node = node.select()
            state.move(action)
        action_probs = self.policy(state)
        winner = state.win(state.chess_Box)
        if not winner:
            node.expand(action_probs)
        leaf_value = self.evaluate(state)
        node.update_recursive(leaf_value)
    
    def evaluate(self, state, limit=100):
        player = state.player
        for i in range(limit):
            winner = state.win(state.chess_Box)
            if winner:
                break
            act_probs = rollout_policy_fn(state)
            max_action = max(act_probs, key=itemgetter(1))[0]
            state.move(max_action)
        else:
            self.logger.info("WARNING: rollout reached move limit")
        return 1 if winner == player else -1
        
    def update_move(self, last):
        if last in self.root.child:
            self.root = self.root.child[last]
            self.root.parent = None
        else:
            self.root = Node(None)

class Mctsplayer():
    def __init__(self, logger):
        self.mcts = Mcts(logger)
        self.logger = logger

    def set_player_ind(self, p):
        self.player = p

    def reset_player(self):
        self.mcts.update_move(-1)

    def get_action(self, board):
        sensible_moves = board.availables
        if len(sensible_moves) > 0:
            move = self.mcts.get_move(board)
            self.mcts.update_move(-1)
            return move
        else:
            self.logger.info("WARNING: the board is full")

