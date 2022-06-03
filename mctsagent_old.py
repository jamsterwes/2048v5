import copy
import math
import time
import random

class Util:
    @staticmethod
    def maxi(items):
        i = 0
        x = 0
        for n, item in enumerate(items):
            if item > x:
                x = item
                i = n
        return i, x


class MCTSRNGNode:
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3

    def __init__(self, board, parent=None):
        self.board = board.fork()
        self.parent = parent
        self.children = [None, None, None, None]
        self.value = 0.0
        self.visits = 0

    def fork_move(self, board, move, rand=True):
        fork = board.fork()
        return fork, self.flat_move(fork, move, rand)
    
    def traverse(self):
        for move in range(4):
            if self.children[move] is None:
                prerand_board, _ = self.fork_move(self.board, move, False)
                self.children[move] = MCTSTreeNode(prerand_board, self) 
            self.children[move].value += self.rollout(self.children[move])
    
    # One unit of simulation
    def rollout(self, leaf):
        fork = self.board.fork()
        fork.add_random()
        # do something...
        


class MCTSUserNode:
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3

    def __init__(self, board, parent=None):
        self.board = board.fork()
        self.parent = parent
        self.children = [None, None, None, None]
        self.value = 0.0
        self.visits = 0

    def flat_move(self, board, move, rand=True):
        if move == self.RIGHT:
            return board.press_right(rand)
        elif move == self.UP:
            return board.press_up(rand)
        elif move == self.LEFT:
            return board.press_left(rand)
        else:
            return board.press_down(rand)

    def fork_move(self, board, move, rand=True):
        fork = board.fork()
        return fork, self.flat_move(fork, move, rand)
    
    def traverse(self):
        for move in range(4):
            if self.children[move] is None:
                prerand_board, _ = self.fork_move(self.board, move, False)
                self.children[move] = MCTSTreeNode(prerand_board, self) 
            self.children[move].value += self.rollout(self.children[move])
    
    # One unit of simulation
    def rollout(self, leaf):
        fork = leaf.board.fork()
        fork.add_random()
        while not fork.no_moves():
            # Run random move
            self.flat_move(fork, random.randint(0, 3))
        if fork.is_win():
            return 1
        else:
            return 0


class MCTSAgent:
    def score(self, board):
        start_time = time.time()
        root = MCTSTreeNode(board)
        # 3 seconds per move
        samples = 0
        while time.time() - start_time < 1.5:
            root.traverse()
            samples += 4
        
        print("Samples this move: {}".format(samples))

        return [node.value for node in root.children]

    def move(self, board):
        right_valid, _ = board.fork().press_right()
        up_valid, _ = board.fork().press_up()
        left_valid, _ = board.fork().press_left()
        down_valid, _ = board.fork().press_down()

        scores = self.score(board)
        movei, maxscore = Util.maxi(scores)

        try:
            nscores = copy.deepcopy(scores)
            nscores.remove(maxscore)
            nextmaxscore = max(nscores)
        except:
            nextmaxscore = maxscore

        if maxscore > 0:
            if movei == MCTSTreeNode.RIGHT:
                board.press_right()
            elif movei == MCTSTreeNode.UP:
                board.press_up()
            elif movei == MCTSTreeNode.LEFT:
                board.press_left()
            else:
                board.press_down()
        else:
            if right_valid:
                board.press_right()
            elif left_valid:
                board.press_left()
            elif up_valid:
                board.press_up()
            elif down_valid:
                board.press_down()
        
        return "L: {:0.2f} R: {:0.2f} U: {:0.2f} D: {:0.2f}  -  M: {:0.2f}".format(scores[MCTSTreeNode.LEFT] * 100, scores[MCTSTreeNode.RIGHT] * 100, scores[MCTSTreeNode.UP] * 100, scores[MCTSTreeNode.DOWN] * 100, maxscore * 100 - nextmaxscore * 100)