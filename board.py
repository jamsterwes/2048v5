import random
import copy
import math

class Board:
    def __init__(self):
        self.pieces = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.add_random()
        self.add_random()
    
    def fork(self):
        return copy.deepcopy(self)
    
    def get_id(self):
        idstr = ""
        for yi in range(4):
            for xi in range(4):
                piece = self.pieces[yi][xi]
                if piece == 0:
                    piece = 1
                idstr += hex(int(math.log2(piece)))[2:]
        return int(idstr, 16)
    
    @staticmethod
    def from_id(idint):
        idstr = hex(idint)[2:]
        pad = 16 - len(idstr)
        idstr = "0" * pad + idstr
        pieces = [[],[],[],[]]
        c = 0
        for yi in range(4):
            for _ in range(4):
                piece = math.pow(2, int(idstr[c], 16))
                if piece == 1:
                    piece = 0
                pieces[yi].append(piece)
                c += 1
        b = Board()
        b.pieces = pieces
        return b

    def _get_spots(self):
        spots = []
        for yi in range(4):
            for xi in range(4):
                if self.pieces[yi][xi] == 0:
                    spots.append([xi,yi])
        return spots

    def no_moves(self):
        if len(self._get_spots()) > 0:
            return False
        if self.fork().press_left(False)[0] > 0:
            return False
        if self.fork().press_up(False)[0] > 0:
            return False
        if self.fork().press_right(False)[0] > 0:
            return False
        if self.fork().press_down(False)[0] > 0:
            return False
        return True
    
    def is_win(self):
        return sum([sum([1 for piece in row if piece >= 2048]) for row in self.pieces]) >= 1

    def _add_random(self, spot, value):
        self.pieces[spot[1]][spot[0]] = value
    
    def add_random(self):
        spots = self._get_spots()
        if len(spots) <= 0:
            return False
        spot = random.choice(self._get_spots())
        value = random.choice([2] * 9 + [4])
        self._add_random(spot, value)
        return True
    
    def add_random_action(self):
        spots = self._get_spots()
        if len(spots) <= 0:
            return None
        spot = random.choice(self._get_spots())
        value = random.choice([2] * 9 + [4])
        self._add_random(spot, value)
        return (spot[0], spot[1], value)

    def press_left(self, add_random=True):
        n = 0
        s = 0
        for row in range(4):
            # Apply piecewise gravity
            for col in range(1, 4):
                maxFall = col
                fall = 1
                while fall <= maxFall:
                    newCol = col - fall
                    oldCol = col - fall + 1
                    if self.pieces[row][newCol] == 0:
                        self.pieces[row][newCol] = self.pieces[row][oldCol]
                        self.pieces[row][oldCol] = 0
                        fall += 1
                        n += 1
                    elif self.pieces[row][newCol] == self.pieces[row][oldCol]:
                        self.pieces[row][newCol] *= 2
                        self.pieces[row][oldCol] = 0
                        fall += 2
                        s += math.log2(self.pieces[row][newCol])
                        n += 1
                    else:
                        fall += 2
        if n > 0 and add_random:
            self.add_random()
        return n, s

    def press_up(self, add_random=True):
        n = 0
        s = 0
        for col in range(4):
            # Apply piecewise gravity
            for row in range(1, 4):
                maxFall = row
                fall = 1
                while fall <= maxFall:
                    newRow = row - fall
                    oldRow = row - fall + 1
                    if self.pieces[newRow][col] == 0:
                        self.pieces[newRow][col] = self.pieces[oldRow][col]
                        self.pieces[oldRow][col] = 0
                        fall += 1
                        n += 1
                    elif self.pieces[newRow][col] == self.pieces[oldRow][col]:
                        self.pieces[newRow][col] *= 2
                        self.pieces[oldRow][col] = 0
                        fall += 2
                        s += math.log2(self.pieces[newRow][col])
                        n += 1
                    else:
                        fall += 2
        if n > 0 and add_random:
            self.add_random()
        return n, s
        
    def press_right(self, add_random=True):
        n = 0
        s = 0
        for row in range(4):
            # Apply piecewise gravity
            for col in reversed(range(3)):
                maxFall = 3 - col
                fall = 1
                while fall <= maxFall:
                    newCol = col + fall
                    oldCol = col + fall - 1
                    if self.pieces[row][newCol] == 0:
                        self.pieces[row][newCol] = self.pieces[row][oldCol]
                        self.pieces[row][oldCol] = 0
                        fall += 1
                        n += 1
                    elif self.pieces[row][newCol] == self.pieces[row][oldCol]:
                        self.pieces[row][newCol] *= 2
                        self.pieces[row][oldCol] = 0
                        fall += 2
                        s += math.log2(self.pieces[row][newCol])
                        n += 1
                    else:
                        fall += 2
        if n > 0 and add_random:
            self.add_random()
        return n, s
        
    def press_down(self, add_random=True):
        n = 0
        s = 0
        for col in range(4):
            # Apply piecewise gravity
            for row in reversed(range(3)):
                maxFall = 3 - row
                fall = 1
                while fall <= maxFall:
                    newRow = row + fall
                    oldRow = row + fall - 1
                    if self.pieces[newRow][col] == 0:
                        self.pieces[newRow][col] = self.pieces[oldRow][col]
                        self.pieces[oldRow][col] = 0
                        fall += 1
                        n += 1
                    elif self.pieces[newRow][col] == self.pieces[oldRow][col]:
                        self.pieces[newRow][col] *= 2
                        self.pieces[oldRow][col] = 0
                        fall += 2
                        s += math.log2(self.pieces[newRow][col])
                        n += 1
                    else:
                        fall += 2
        if n > 0 and add_random:
            self.add_random()
        return n, s