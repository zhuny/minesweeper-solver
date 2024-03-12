from puzzle.game import MinesweeperWindowInterface
from puzzle.game_pygame import PygameInterface
from puzzle.solver import MinesweeperSolver


def main():
    # 30/20/100
    w, h = 49, 26
    # MinesweeperWindowInterface().save_digit()
    MinesweeperSolver(
        PygameInterface(w, h, w * h // 6)
    ).solve(20)


if __name__ == '__main__':
    main()
