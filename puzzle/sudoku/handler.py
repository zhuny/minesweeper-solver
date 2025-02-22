import random

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


class GenerateProblemClickHandler(EventHandler):
    """
    선택한 셀에 값을 넣는 문제를 생성한다.
    """

    def handle(self):
        from puzzle.sudoku.data import CandidateCell, SudokuWorldData

        data: SudokuWorldData = self.target
        self.target.message = ""

        while True:
            for cell in data.cell_info.values():
                cell.child = CandidateCell(
                    candidate_list=list(range(1, data.size + 1))
                )
            yield

            yield from self.set_all()
            if self.target.is_valid():
                break
            ClearCellClickHandler(target=self.target).handle()

    def set_all(self):
        for cell in self.target.cell_info.values():
            if not cell.is_selected:
                continue

            if cell.is_candidate():
                if not self.pick_random(cell):
                    return

            yield

    def pick_random(self, cell):
        pick = random.choice(cell.child.candidate_list)
        return self.target.set_value(cell.x, cell.y, pick)


class ClearCellClickHandler(EventHandler):
    def handle(self):
        from puzzle.sudoku.data import OneNumberCell

        self.target.message = ""

        for cell in self.target.cell_info.values():
            cell.child = OneNumberCell()


class SolveUniqueClickHandler(EventHandler):
    def handle(self):
        self.target.message = ""

        count = 0
        for is_solved in self.travel([]):
            yield from self.wait(1)
            if is_solved:
                count += 1
                if count == 2:
                    self.target.message = 'Multiple solutions'
                    yield
                    return
                if count == 1:
                    self.target.message = 'One found'

        if count == 0:
            self.target.message = 'No solutions'
        yield

    def travel(self, stack):
        cell = self.get_candidate_cell()
        if cell is None:
            yield True
            return

        for num in list(cell.child.candidate_list):
            self.push_data(stack)
            if self.target.set_value(cell.x, cell.y, num):
                yield False
                yield from self.travel(stack)
            self.pop_data(stack)
            yield False

    def get_candidate_cell(self):
        counter = {}

        for cell in self.target.cell_info.values():
            if cell.is_candidate():
                counter.setdefault(
                    len(cell.child.candidate_list),
                    cell
                )

        if counter:
            return counter[min(counter)]

    def push_data(self, stack):
        candidate_map = {}
        for cell in self.target.cell_info.values():
            if cell.is_candidate():
                candidate_map[cell.x, cell.y] = list(cell.child.candidate_list)
        stack.append(candidate_map)

    def pop_data(self, stack):
        from puzzle.sudoku.data import CandidateCell

        candidate_map = stack.pop()
        for k, candidate in candidate_map.items():
            cell = self.target.cell_info[k]
            cell.child = CandidateCell(candidate_list=candidate)


class CompleteProblemClickHandler(EventHandler):
    def handle(self):
        from puzzle.sudoku.data import OneNumberCell

        for cell in self.target.cell_info.values():
            if not cell.is_selected:
                cell.child = OneNumberCell()


class AutoGenerateClickHandler(EventHandler):
    def handle(self):
        while True:
            yield from GenerateProblemClickHandler(target=self.target).handle()
            yield from SolveUniqueClickHandler(target=self.target).handle()
            if self.target.message == 'One found':
                CompleteProblemClickHandler(target=self.target).handle()
                yield
                return
            ClearCellClickHandler(target=self.target).handle()
            yield
