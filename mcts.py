'''
@Author: your name
@Date: 2020-07-20 19:19:35
@LastEditTime: 2020-07-20 22:06:10
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /Gobang/mcts.py
'''
class Node():
    def __init__(self):
        self.parent = None
        self.child = {}
        self.visits = 0
        self.value = 0.0
    
    def expand(self):
        pass
    
    def select(self):
        pass

    def update(self, value):
        self.value += value
        self.visits += 1

    def update_recursive(self, value):
        if self.parent:
            self.parent.update_recursive()
        self.update(value)

    def get_value(self):
        pass

    def is_leaf(self):
        pass

    def is_root(self):
        pass

class Mcts():
    def __init__(self):
        self.root = Node()
    
    
    
    def play_out(self, state):
        node = self.root
        while not node.is_leaf():
            action, node = node.select(state)
            state.move(action)
        action_probs = self.policy(state)
        end, winner = state.game_end()
        if not end:
            node.expand(action_probs)
        leaf_value = self.evaluate(state)
        node.update_recursive(leaf_value)
    
    def evaluate(self, state, limit=1000):
        player = state.player()
        for i in range(limit):
            end, winner = state.game_end()
            if end:
                break
            action_probs = self.policy(state)
            max_action = max(action_probs, key=itemgetter(1))[0]
            state.move(max_action)
        else:
            print("WARNING: rollout reached move limit")
        if winner == -1:
            return 0
        else:
            return 1 if winner == player else -1
        
    def update_move(self, last):
        if last in self.root.child:
            self.root = self.root.child[last]
            self.root.parent = None
        else:
            self.root = Node()

class Mctsplayer():
    def __init__(self):

