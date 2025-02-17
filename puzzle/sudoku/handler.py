from core.handler import EventHandler


class TableCellClickHandler(EventHandler):
    """
    Table의 cell의 선택 toggle하는 handler
    선택이 되면, 문제를 만들 때, 해당 셀에 값을 정하게 된다.
    """
    def handle(self):
        from puzzle.sudoku.data import SudokuCell

        cell: SudokuCell = self.target
        cell.is_selected = not cell.is_selected
