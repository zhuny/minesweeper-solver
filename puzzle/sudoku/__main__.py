from puzzle.sudoku.world import (SudokuWorldDrawer)
from puzzle.sudoku.data import SudokuWorldData
from puzzle.sudoku.solver import SudokuWorldSolver


def main():
    width = 1440
    SudokuWorldDrawer(
        data=SudokuWorldData(row=4, col=3),
        solver=SudokuWorldSolver(),
        screen_size=(width, width * 9 // 16)
    ).main_loop()


if __name__ == '__main__':
    main()
