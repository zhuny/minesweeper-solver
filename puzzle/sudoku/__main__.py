from puzzle.sudoku.world import (SudokuWorldDrawer)
from puzzle.sudoku.data import SudokuWorldData
from puzzle.sudoku.solver import SudokuWorldSolver


def main():
    SudokuWorldDrawer(
        data=SudokuWorldData(row=4, col=3),
        solver=SudokuWorldSolver()
    ).main_loop()


if __name__ == '__main__':
    main()
