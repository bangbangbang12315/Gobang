'''
@Author: DB
@Date: 2020-07-06 12:45:33
@LastEditTime: 2020-07-18 22:03:30
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /wuziqi/minimax.py
'''
import sys
import numpy as np
import json
import copy
class Chess():
    def __init__(self):
        self.length = 15
        self.debug = False
        self.player = 1
        self.chess_Box = self.loadChess()
        if self.debug:
            self.check(self.chess_Box)

    def loadChess(self):
        if not self.debug:
            tmp = sys.argv[1]
            box = tmp.strip().split(',')
            box = list(map(lambda x: int(x), box))
            grid = [[0] * self.length for i in range(self.length)]
            for i in range(self.length):
                for j in range(self.length):
                    grid[i][j] = box[i * 15 + j]
        else:
            grid = [[0] * self.length for i in range(self.length)]
            grid[7][8] = 1
        grid = np.array(grid)
        return grid
    
    def isTerminalwindow(self, window):
        return window.count(1) == 5 or window.count(2) == 5

    
    def win(self, grid):
        flatten = list(grid.flatten())
        if flatten.count(0) == 0:
            return True
        for row in range(self.length):
            for col in range(self.length - 4):
                window = list(grid[row, col:col+5])
                if self.isTerminalwindow(window):
                    return True
        for col in range(self.length):
            for row in range(self.length - 4):
                window = list(grid[row:row+5,col])
                if self.isTerminalwindow(window):
                    return True

        for row in range(self.length - 4):
            for col in range(self.length - 4):
                window = list(grid[range(row, row + 5), range(col, col + 5)])
                if self.isTerminalwindow(window):
                    return True

        for row in range(4, self.length):
            for col in range(self.length - 4):
                window = list(grid[range(row, row - 5, -1), range(col, col + 5)])
                if self.isTerminalwindow(window):
                    return True
        return False

    def neighbor(self, grid, x, y, dis):
        for i in range(x - dis, x + dis + 1):
            for j in range(y - dis, y + dis + 1):
                if i < 0 or i > 14 or j < 0 or j > 14:
                    continue
                if grid[i,j]:
                    return True
        return False
                
    def genCandidate(self, grid, depth):
        candidate = []
        for i in range(self.length):
            for j in range(self.length):
                if grid[i,j] == 0 and self.neighbor(grid, i, j, depth):
                    candidate.append((i,j))
        return candidate

    def check_window(self, window, num_discs, piece):
        return (window.count(piece) == num_discs and window.count(0) == 5 - num_discs)
    
    def count_windows(self, grid, num_discs, piece):
        num_windows = 0
        # horizontal
        for row in range(self.length):
            for col in range(self.length - 4):
                window = list(grid[row, col:col + 5])
                if self.check_window(window, num_discs, piece):
                    num_windows += 1
        # vertical
        for row in range(self.length - 4):
            for col in range(self.length):
                window = list(grid[row:row+5, col])
                if self.check_window(window, num_discs, piece):
                    num_windows += 1
        # positive diagonal
        for row in range(self.length - 4):
            for col in range(self.length - 4):
                window = list(grid[range(row, row + 5), range(col, col + 5)])
                if self.check_window(window, num_discs, piece):
                    num_windows += 1
        # negative diagonal
        for row in range(4, self.length):
            for col in range(self.length - 4):
                window = list(grid[range(row, row - 5, -1), range(col, col + 5)])
                if self.check_window(window, num_discs, piece):
                    num_windows += 1
        return num_windows
    
    def evaluate(self, grid, mark):
        num_threes = self.count_windows(grid, 3, mark)
        num_fours = self.count_windows(grid, 4, mark)
        num_fives = self.count_windows(grid, 5, mark)
        num_threes_opp = self.count_windows(grid, 3, mark%2+1)
        num_fours_opp = self.count_windows(grid, 4, mark%2+1)
        num_fives_opp = self.count_windows(grid, 5, mark%2+1)
        score = num_threes - 10*num_threes_opp - 1e2*num_fours_opp + 1e3*num_fours - 1e4*num_fives_opp + 1e5*num_fives
        return score

    def drop(self, grid, x, y, mark):
        child = copy.deepcopy(grid)
        child[x, y] = mark
        return child

    def miniMax(self, grid, depth, maximizingPlayer, mark):
        isterminal = self.win(grid)
        candidate = self.genCandidate(grid, depth)
        if depth == 0 or isterminal:
            return self.evaluate(grid, mark)
        if maximizingPlayer:
            value = -np.Inf
            for p in candidate:
                child = self.drop(grid, p[0], p[1], mark)
                value = max(value, self.miniMax(child, depth-1, False, mark))
        else:
            value = np.Inf
            for p in candidate:
                child = self.drop(grid, p[0], p[1], mark%2+1)
                value = min(value, self.miniMax(child, depth-1, True, mark))
        return value
    
    def alphaBeta(self, grid, depth, alpha, beta, maximizingPlayer, mark):
        isterminal = self.win(grid)
        candidate = self.genCandidate(grid, depth)
        if depth == 0 or isterminal:
            return self.evaluate(grid, mark)
        if maximizingPlayer:
            for p in candidate:
                child = self.drop(grid, p[0], p[1], mark)
                alpha = max(alpha, self.alphaBeta(child, depth-1, alpha, beta, False, mark))
                if alpha >= beta:
                    return beta
            return alpha
        else:
            for p in candidate:
                child = self.drop(grid, p[0], p[1], mark%2+1)
                beta = min(beta, self.alphaBeta(child, depth-1, alpha, beta, True, mark))
                if beta <= alpha:
                    return alpha
            return beta

        


    def score_move_improvement(self, grid, x, y, mark, nsteps):
        next_grid = self.drop(grid, x, y, mark)
        # score = self.miniMax(next_grid, nsteps-1, False, mark)
        alpha = -np.inf
        beta = np.inf
        score = self.alphaBeta(next_grid, nsteps-1, alpha, beta, False, mark)
        return score
        
    def agent(self):
        candidate = self.genCandidate(self.chess_Box, 2)
        scores = dict(zip(candidate, [self.score_move_improvement(self.chess_Box, p[0], p[1], self.player, 1) for p in candidate]))
        max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]
        if self.debug:
            with open('candidate', 'w') as f:
                for i in range(self.length):
                    for j in range(self.length):
                        if (i,j) not in scores:
                            f.write(str(self.chess_Box[i][j])+'\t')
                        else:
                            f.write(str(scores[(i,j)])+'\t')
                    f.write('\n')
        print(100 * max_cols[0][0] + max_cols[0][1])

    def check(self, x):
        with open('test', 'w') as t:
            for col in x:
                for w in col:
                    t.write(str(w) + '\t')
                t.write('\n')
            
if __name__ == "__main__":
    chess = Chess()
    chess.agent()