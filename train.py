from mctsagent import MCTSAgent
import pickle
import math
import random
from board import Board
from os import path

def train(board):
    agent = MCTSAgent(Board.from_id(board), False)
    agent.score(0.01)
    return agent.root.total_score, agent.root.n

# prog len = 32 char
def drawprogress(prefix, pct, postfix):
    out = "["
    lenint = max(0, math.ceil(pct * 32) - 1)
    out += "=" * lenint + ">" + " " * (31 - lenint) + "]"
    print(prefix + out + postfix)

def trainall():
    data = pickle.load(open("mcts.db", "rb"))
    boards = list(data.keys())
    random.shuffle(boards)
    for i, board in enumerate(boards):
        percent = i / len(boards)
        t, n = train(board)
        drawprogress("{}/{} ".format(i + 1, len(boards)), percent, "avg: {} (x{})".format(t / n, n))
        

if __name__ == "__main__":
    while True:
        trainall()