from puzzle.game_pygame import PygameInterface
from puzzle.solver import MinesweeperSolver


def main():
    w, h = 59, 31
    MinesweeperSolver(
        PygameInterface(w, h, w * h // 6)
    ).solve(20)


if __name__ == '__main__':
    main()
