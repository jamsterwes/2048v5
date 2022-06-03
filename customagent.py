import copy
import math

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


class CustomAgent:
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3

    def __init__(self, samples, depth):
        self.SAMPLES = samples
        self.DEPTH = depth

    def fork_move(self, board, move):
        fork = board.fork()
        if move == self.RIGHT:
            return fork, fork.press_right()
        elif move == self.UP:
            return fork, fork.press_up()
        elif move == self.LEFT:
            return fork, fork.press_left()
        else:
            return fork, fork.press_down()

    FULL_PENALTY = 4
    def score(self, board, move, d=1, s=None):
        if s is None:
            s = self.SAMPLES
        cumscore = 0
        for n in range(s):
            if d >= self.DEPTH:
                fork, moveres = self.fork_move(board, move)
                if moveres[0] > 0:
                    cumscore += moveres[1]
                    # TODO: modulate this coefficient (err on side of higher)
                    cumscore -= 0.0625 * self.FULL_PENALTY * sum([sum([1 for piece in row if piece != 0]) for row in fork.pieces])
                else:
                    cumscore -= 1
            else:
                fork, moveres = self.fork_move(board, move)
                if moveres[0] > 0:
                    for next_move in range(4):
                        cumscore += self.score(fork, next_move, d + 1, math.ceil(s / 2)) * 0.25
                else:
                    cumscore -= 1
        return cumscore / s

    def move(self, board):
        right_valid, right_score = board.fork().press_right()
        up_valid, up_score = board.fork().press_up()
        left_valid, left_score = board.fork().press_left()
        down_valid, down_score = board.fork().press_down()

        scores = [self.score(board, move) for move in range(4)]
        movei, maxscore = Util.maxi(scores)

        try:
            nscores = copy.deepcopy(scores)
            nscores.remove(maxscore)
            nextmaxscore = max(nscores)
        except:
            nextmaxscore = maxscore

        if maxscore > 0:
            if movei == self.RIGHT:
                board.press_right()
            elif movei == self.UP:
                board.press_up()
            elif movei == self.LEFT:
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
        
        return "L: {:0.2f} R: {:0.2f} U: {:0.2f} D: {:0.2f}  -  M: {:0.2f}".format(scores[self.LEFT] * 100, scores[self.RIGHT] * 100, scores[self.UP] * 100, scores[self.DOWN] * 100, maxscore * 100 - nextmaxscore * 100)