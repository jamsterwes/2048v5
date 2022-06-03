import copy
import math
import time
import random
import pickle
from os import path

class Util:
    @staticmethod
    def maxi(items):
        i = 0
        x = -math.inf
        for n, item in enumerate(items):
            if item > x:
                x = item
                i = n
        return i, x


class MCTSPickleNode:
    def __init__(self, treeNode=None):
        if treeNode is not None:
            self.t = treeNode.total_score
            self.n = treeNode.n

    @staticmethod
    def from_data(data):
        node = MCTSPickleNode()
        node.t = data[0]
        node.n = data[1]
        return node
    
    def to_data(self):
        return (self.t, self.n)


class MCTSTreeNode:
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3

    def __init__(self, board, parent=None, is_rng=False):
        self.parent = parent
        self.board = board
        self.is_rng = is_rng
        self.children = []
        self.total_score = 0
        self.n = 0
        self.spot_mapping = {}

    # Apply move to own board
    def flat_move(self, board, move, rand=True):
        if move == self.RIGHT:
            return board.press_right(rand)
        elif move == self.UP:
            return board.press_up(rand)
        elif move == self.LEFT:
            return board.press_left(rand)
        else:
            return board.press_down(rand)

    # Make new copy of board then apply move to it
    def fork_move(self, board, move, rand=True):
        fork = board.fork()
        return fork, self.flat_move(fork, move, rand)

    # Get UCB1 for this node
    def ucb1(self):
        if self.n == 0 or self.parent.n == 0:
            return math.inf
        else:
            return (self.total_score / self.n) + 2 * math.sqrt(math.log(self.parent.n) / self.n)

    # Get child by action
    def by_action(self, action):
        try:
            if self.is_rng:
                return self.children[self.spot_mapping[action]]
            else:
                return self.children[action]
        except Exception as e:
            print(e)
            return None

    # Create children
    def birth(self):
        if self.is_rng:
            spots = self.board._get_spots()
            if len(spots) <= 0:
                return
            for spot in spots:
                board2 = self.board.fork()
                board2._add_random(spot, 2)

                self.spot_mapping[(spot[0], spot[1], 2)] = len(self.children)
                self.children.append(MCTSTreeNode(board2, self, False))

                board4 = self.board.fork()
                board4._add_random(spot, 4)

                self.spot_mapping[(spot[0], spot[1], 4)] = len(self.children)
                self.children.append(MCTSTreeNode(board4, self, False))
        else:
            for move in range(4):
                board, movetup = self.fork_move(self.board, move, False)
                if movetup[0] > 0:
                    self.children.append(MCTSTreeNode(board, self, True))
                else:
                    self.children.append(None)
    
    # Rollout algo
    def rollout(self):
        si = self
        d = 0
        while True:
            d += 1
            if si.board.is_win():
                return 1000000

            if si.board.no_moves():
                if si.board.is_win():
                    return 1000000
                else:
                    return d
            else:
                if si.is_rng:
                    fork = si.board.fork()
                    if fork.add_random():
                        si = MCTSTreeNode(fork, si, False)
                    else:
                        if si.board.is_win():
                            return 1000000
                        else:
                            return d
                else:
                    fork, _ = self.fork_move(si.board, random.randint(0, 3), False)
                    si = MCTSTreeNode(fork, si, True)
                


class MCTSAgent:
    def __init__(self, board, verbose=True):
        if path.exists("mcts.db"):
            self.data = pickle.load(open("mcts.db", "rb"))
            if verbose:
                print("Loaded {} states from db!".format(len(self.data)))
        else:
            self.data = {}
        self.root = MCTSTreeNode(board)        

    def ucbnode(self, node):
        if node is None:
            return -10000
        else:
            return node.ucb1()
    
    def nnode(self, node):
        if node is None:
            return -100
        else:
            return node.n

    def score(self, think_time=0.1):
        start_time = time.time()

        # if 512 in sum(self.root.board.pieces, []) and 1024 in sum(self.root.board.pieces, []):
        #     think_time = 0.125

        # print(self.root.board.get_id())
        # print("Root: {}".format(self.root.board.pieces))
        if len(self.root.children) <= 0:
            self.root.birth()

        while time.time() - start_time < think_time:
            self.board_ref.handle_events()
            current = self.root
            while len(current.children) > 0:
                current.n += 1
                ucbs = [self.ucbnode(node) for node in current.children]
                maxi, maxval = Util.maxi(ucbs)
                current = current.children[maxi]
            # We are leaf/terminal node
            if current.n <= 0 or current.board.no_moves():
                board_id = current.board.get_id()
                if board_id in self.data:
                    pickleNode = MCTSPickleNode.from_data(self.data[board_id])
                    current.n = pickleNode.n
                    current.total_score = pickleNode.t
                current.n += 1
                rollout_score = current.rollout()
                current.total_score += rollout_score
                self.data[current.board.get_id()] = MCTSPickleNode(current).to_data()
                # Backprop
                while current.parent is not None:
                    current = current.parent
                    current.total_score += rollout_score
            # We are branch node
            else:
                current.n += 1
                # Expand
                if len(current.children) <= 0:
                    current.birth()
                # Get first valid child
                for child in current.children:
                    if child is not None:
                        current = child
                        break
                current.n += 1
                rollout_score = current.rollout()
                current.total_score += rollout_score
                # Backprop
                while current.parent is not None:
                    current = current.parent
                    current.total_score += rollout_score
        
        # Update database of roots
        self.data[self.root.board.get_id()] = MCTSPickleNode(self.root).to_data()
        pickle.dump(self.data, open("mcts.db", "wb"))

        return [self.nnode(node) for node in self.root.children]

    def move(self):
        right_valid, _ = self.root.board.fork().press_right()
        up_valid, _ = self.root.board.fork().press_up()
        left_valid, _ = self.root.board.fork().press_left()
        down_valid, _ = self.root.board.fork().press_down()

        scores = self.score()
        movei, maxscore = Util.maxi(scores)

        if maxscore <= 0:
            if right_valid:
                movei = MCTSTreeNode.RIGHT
            elif left_valid:
                movei = MCTSTreeNode.LEFT
            elif up_valid:
                movei = MCTSTreeNode.UP
            elif down_valid:
                movei = MCTSTreeNode.DOWN
        
        if movei == MCTSTreeNode.RIGHT:
            self.root.board.press_right(False)
        elif movei == MCTSTreeNode.UP:
            self.root.board.press_up(False)
        elif movei == MCTSTreeNode.LEFT:
            self.root.board.press_left(False)
        else:
            self.root.board.press_down(False)
        
        # Get node for moving
        newroot = self.root.by_action(movei)
        # If none here, we can just add random and recreate root
        if newroot is None:
            self.root.board.add_random()
            self.root = MCTSTreeNode(self.root.board)
            if self.root is None:
                print("ROOT SET FROM LINE 214")
        else:
            act = newroot.board.fork().add_random_action()
            if act is None:
                self.root.board.add_random()
                self.root = MCTSTreeNode(self.root.board)
                if self.root is None:
                    print("ROOT SET FROM LINE 221")
            else:
                newroot = newroot.by_action(act)
                if newroot is None:
                    self.root.board.add_random()
                    self.root = MCTSTreeNode(self.root.board)
                    if self.root is None:
                        print("ROOT SET FROM LINE 228")
                else:
                    self.root = newroot
                    if self.root is None:
                        print("ROOT SET FROM LINE 232")
        
        return "L: {} R: {} U: {} D: {}".format(scores[MCTSTreeNode.LEFT], scores[MCTSTreeNode.RIGHT], scores[MCTSTreeNode.UP], scores[MCTSTreeNode.DOWN])