import functools

import pydantic

from core.drawer import (ConstantGapInfo, GapListInfo,
                         RectangleTextDrawer,
                         TableCellInfo, TableDrawer)
from core.theme import Theme
from core.world import WorldData
from puzzle.sudoku.handler import TableCellClickHandler


class CandidateCell(pydantic.BaseModel):
    candidate_list: list[int] = pydantic.Field(default_factory=list)
    candidate_set: set[int] = pydantic.Field(default_factory=set, init=False)

    def model_post_init(self, __context):
        self.candidate_set.update(self.candidate_list)

    def build(self,
              theme: Theme, root: 'SudokuWorldData',
              parent, color, is_selected):
        return TableDrawer(
            cell_width=root.row, cell_height=root.col,
            row_gap=ConstantGapInfo(value=0),
            col_gap=ConstantGapInfo(value=0),
            color=color,
            cell_list=[
                self._build_cell(i, theme, root)
                for i in range(1, root.size + 1)
            ]
        )

    def remove(self, value):
        if value in self.candidate_set:
            self.candidate_set.remove(value)
            self.candidate_list.remove(value)

    def _build_cell(self, index, theme, root):
        y, x = divmod(index - 1, root.row)
        return TableCellInfo(
            x=x, y=y,
            drawer=RectangleTextDrawer(
                width=16, height=16,
                text=index if index in self.candidate_set else "",
                text_size=16, text_color="#777777"
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
            width=50, height=50,
            color=color,
            text=self.value,
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


class SudokuWorldData(WorldData):
    row: int
    col: int

    cell_info: dict[tuple[int, int], SudokuCell] = pydantic.Field(
        default_factory=dict
    )

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
