import functools

import pydantic

from core.drawer import GapListInfo, RectangleDrawer, TableCellInfo, TableDrawer
from core.world import WorldData


class SudokuCell(pydantic.BaseModel):
    x: int
    y: int

    value: int | None = None
    is_selected: bool = False
    is_fixed: bool = False
    is_set: bool = False
    candidate_list: list[int] = pydantic.Field(default_factory=list)

    def build(self):
        return TableCellInfo(
            x=self.x, y=self.y,
            drawer=RectangleDrawer(width=50, height=50, color=(0, 0, 0))
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

    def build(self):
        return TableDrawer(
            cell_list=[
                cell.build()
                for cell in self.cell_info.values()
            ],
            row_gap=self._build_gap(self.row),
            col_gap=self._build_gap(self.col),
            color=(191, 191, 191),
            cell_width=self.size, cell_height=self.size
        )

    def _build_gap(self, step):
        gap_list = [8] * (self.size + 1)
        for pos in range(0, self.size + 1, step):
            gap_list[pos] = 20
        return GapListInfo(value=gap_list)
