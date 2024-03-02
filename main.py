from puzzle.game import MinesweeperWindowInterface
from puzzle.solver import MinesweeperSolver


def main():
    # MinesweeperWindowInterface().save_digit()
    MinesweeperSolver(
        MinesweeperWindowInterface()
    ).solve()


if __name__ == '__main__':
    main()
