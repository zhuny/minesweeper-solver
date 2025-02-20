from puzzle.sudoku.world import (SudokuWorldDrawer)
from puzzle.sudoku.data import SudokuWorldData
from puzzle.sudoku.solver import SudokuWorldSolver


def main():
    SudokuWorldDrawer(
        data=SudokuWorldData(row=3, col=3),
        solver=SudokuWorldSolver(),
        screen_size=(1024, 600)
    ).main_loop()


if __name__ == '__main__':
    main()
