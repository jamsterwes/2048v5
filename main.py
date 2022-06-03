from customagent import CustomAgent
from mctsagent import MCTSAgent
from board import Board
from renderer import GameRenderer
import sys

def main():
    while True:
        board = Board()
        renderer = GameRenderer(board, MCTSAgent(board))
        movec = 0
        while True:
            movec += 1
            score_line = renderer.run_agent()
            renderer.draw(score_line)
            if renderer.board.is_win():
                print("Win in {} moves".format(movec))
                break
            if renderer.board.no_moves():
                print("Loss in {} moves".format(movec))
                break

if __name__ == "__main__":
    main()