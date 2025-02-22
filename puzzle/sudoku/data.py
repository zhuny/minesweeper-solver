import collections
import functools

import pydantic

from core.drawer import (CenteredRectangle, ConstantGapInfo, GapListInfo,
                         RectangleTextDrawer,
                         TableCellInfo, TableDrawer)
from core.theme import Theme
from core.world import WorldData
from puzzle.sudoku.handler import TableCellClickHandler
from puzzle.sudoku.rule.grouping import BoxGroup, ColGroup, RowGroup


def num_to_text(num: int | None) -> str:
    if num is None:
        return ''
    elif num < 10:
        return str(num)
    else:
        return chr(ord('A') + num - 10)


class CandidateCell(pydantic.BaseModel):
    candidate_list: list[int] = pydantic.Field(default_factory=list)
    candidate_set: set[int] = pydantic.Field(default_factory=set, init=False)

    def model_post_init(self, __context):
        self.candidate_set.update(self.candidate_list)

    def build(self,
              theme: Theme, root: 'SudokuWorldData',
              parent, color, is_selected):
        return CenteredRectangle(
            child=TableDrawer(
                cell_width=root.row, cell_height=root.col,
                row_gap=ConstantGapInfo(value=0),
                col_gap=ConstantGapInfo(value=0),
                cell_list=[
                    self._build_cell(i, theme, root)
                    for i in range(1, root.size + 1)
                ]
            ),
            width=48, height=48,
            color=color
        )

    def remove(self, value):
        if value in self.candidate_set:
            self.candidate_set.remove(value)
            self.candidate_list.remove(value)

    def _build_cell(self, index, theme, root):
        y, x = divmod(index - 1, root.row)
        size = 48 // max(root.row, root.col)
        return TableCellInfo(
            x=x, y=y,
            drawer=RectangleTextDrawer(
                width=size, height=size,
                text=num_to_text(index) if index in self.candidate_set else "",
                text_size=size + 4, text_color="#777777"
            )
        )


class OneNumberCell(pydantic.BaseModel):
    value: int | None = None
    # 수정이 가능한지 여부.
    # 문제에서 제시한 힌트라 수정할 수 없는 경우 True
    # 값이 지정되지 않은 경우 False
    is_fixed: bool = True

    def build(self, theme: Theme, root, parent, color, is_selected):
        return RectangleTextDrawer(
            width=48, height=48,
            color=color,
            text=num_to_text(self.value),
            text_size=30,
            text_color=self._get_text_color(theme, is_selected),
            on_click=[TableCellClickHandler(target=parent)]
        )

    def _get_text_color(self, theme, is_select):
        if self.is_fixed:
            if is_select:
                return theme.color.on_primary
            else:
                return theme.color.on_surface
        else:
            return theme.color.secondary


class SudokuCell(pydantic.BaseModel):
    x: int
    y: int

    child: CandidateCell | OneNumberCell = OneNumberCell()
    is_selected: bool = False  # 퍼즐을 푸는 상황과 상관없이 해당 셀을 강조하고 싶을 때

    def build(self, theme: Theme, root):
        if self.is_selected:
            color = theme.color.primary
        else:
            color = theme.color.surface

        return TableCellInfo(
            x=self.x, y=self.y,
            drawer=self.child.build(theme, root, self, color, self.is_selected)
        )

    def is_candidate(self):
        return isinstance(self.child, CandidateCell)


class SudokuWorldData(WorldData):
    row: int
    col: int

    cell_info: dict[tuple[int, int], SudokuCell] = pydantic.Field(
        default_factory=dict
    )

    message: str = ""

    @functools.cached_property
    def size(self):
        return self.row * self.col

    def model_post_init(self, __context) -> None:
        for x in range(self.size):
            for y in range(self.size):
                self.cell_info[x, y] = SudokuCell(x=x, y=y)

    def build(self, theme: Theme, root):
        return TableDrawer(
            cell_list=[
                cell.build(theme, root)
                for cell in self.cell_info.values()
            ],
            row_gap=self._build_gap(self.row),
            col_gap=self._build_gap(self.col),
            color=theme.color.on_background,
            cell_width=self.size, cell_height=self.size
        )

    def _build_gap(self, step):
        gap_list = [4] * (self.size + 1)
        for pos in range(0, self.size + 1, step):
            gap_list[pos] = 10
        return GapListInfo(value=gap_list)

    def set_value(self, x, y, value):
        # 규칙에 따라 지우기
        for cell in self.cell_info.values():
            if cell.x == x and cell.y == y:
                cell.child = OneNumberCell(value=value)
            elif self.is_match(cell, x, y) and cell.is_candidate():
                cell.child.remove(value)

        # 확정된 값 세팅
        for cell in self.cell_info.values():
            if cell.is_candidate():
                if len(cell.child.candidate_list) == 1:
                    self.set_value(cell.x, cell.y, cell.child.candidate_list[0])

        return self.is_valid()

    def is_match(self, cell, x, y):
        for g in self._grouping():
            if g.key(cell.x, cell.y) == g.key(x, y):
                return True
        return False

    def is_valid(self):
        # 칸에 넣을 숫자가 없는 경우
        for cell in self.cell_info.values():
            if cell.is_candidate():
                if len(cell.child.candidate_list) == 0:
                    return False

        # 숫자를 넣을 칸이 없는 경우
        group_number_count = collections.defaultdict(set)
        for cell in self.cell_info.values():
            number_list = []
            if isinstance(cell.child, CandidateCell):
                number_list.extend(cell.child.candidate_list)
            elif isinstance(cell.child, OneNumberCell):
                number_list.append(cell.child.value)

            for g in self._grouping():
                for number in number_list:
                    group_number_count[g, g.key(cell.x, cell.y)].add(number)

        for ns in group_number_count.values():
            if len(ns) != self.size:
                return False

        return True

    def _grouping(self):
        yield RowGroup(self.row, self.col)
        yield ColGroup(self.row, self.col)
        yield BoxGroup(self.row, self.col)
