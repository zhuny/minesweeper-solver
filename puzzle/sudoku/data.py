import functools

import pydantic

from core.drawer import (GapListInfo, RectangleTextDrawer,
                         TableCellInfo, TableDrawer)
from core.theme import Theme
from core.world import WorldData
from puzzle.sudoku.handler import TableCellClickHandler


class CandidateCell(pydantic.BaseModel):
    candidate_list: list[int] = pydantic.Field(default_factory=list)


class OneNumberCell(pydantic.BaseModel):
    value: int | None = None
    # 수정이 가능한지 여부.
    # 문제에서 제시한 힌트라 수정할 수 없는 경우 True
    # 값이 지정되지 않은 경우 False
    is_fixed: bool = True

    def build(self, theme: Theme, is_selected, parent):
        return RectangleTextDrawer(
            width=50, height=50,
            color=(
                theme.color.primary
                if is_selected else
                theme.color.surface
            ),
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

    def build(self, theme: Theme):
        return TableCellInfo(
            x=self.x, y=self.y,
            drawer=self.child.build(theme, self.is_selected, self)
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

    def build(self, theme: Theme):
        return TableDrawer(
            cell_list=[
                cell.build(theme)
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
