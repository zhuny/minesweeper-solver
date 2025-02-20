import random

from core.handler import EventHandler


class GroupSetting:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def key(self, x, y):
        raise NotImplementedError(self)


class RowGroup(GroupSetting):
    def key(self, x, y):
        return x


class ColGroup(GroupSetting):
    def key(self, x, y):
        return y


class BoxGroup(GroupSetting):
    def key(self, x, y):
        return x // self.row, y // self.col


class TableCellClickHandler(EventHandler):
    """
    Table의 cell의 선택 toggle하는 handler
    선택이 되면, 문제를 만들 때, 해당 셀에 값을 정하게 된다.
    """
    def handle(self):
        from puzzle.sudoku.data import SudokuCell

        cell: SudokuCell = self.target
        cell.is_selected = not cell.is_selected


class GenerateProblemClickHandler(EventHandler):
    """
    선택한 셀에 값을 넣는 문제를 생성한다.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._grouping = [
            RowGroup(self.target.row, self.target.col),
            ColGroup(self.target.row, self.target.col),
            BoxGroup(self.target.row, self.target.col)
        ]

    def handle(self):
        from puzzle.sudoku.data import CandidateCell, SudokuWorldData

        data: SudokuWorldData = self.target

        for cell in data.cell_info.values():
            cell.child = CandidateCell(
                candidate_list=list(range(1, data.size + 1))
            )
        yield

        for cell in data.cell_info.values():
            if not cell.is_selected:
                continue

            self.pick_random(cell)
            yield

    def pick_random(self, cell):
        pick = random.choice(cell.child.candidate_list)
        self.set_value(cell.x, cell.y, pick)

    def set_value(self, x, y, value):
        from puzzle.sudoku.data import OneNumberCell, CandidateCell

        for cell in self.target.cell_info.values():
            if cell.x == x and cell.y == y:
                cell.child = OneNumberCell(value=value)
            elif self.is_match(cell, x, y) and isinstance(cell.child,
                                                          CandidateCell):
                cell.child.remove(value)

    def is_match(self, cell, x, y):
        for g in self._grouping:
            if g.key(cell.x, cell.y) == g.key(x, y):
                return True
        return False

    def _frame(self, n):
        for i in range(n):
            yield i


class ClearCellClickHandler(EventHandler):
    def handle(self):
        from puzzle.sudoku.data import OneNumberCell

        for cell in self.target.cell_info.values():
            cell.child = OneNumberCell()
