from core.drawer import (ConstantExcludeGapInfo, LayerDirection, LayerDrawer,
                         RectangleTextDrawer)
from core.theme import Theme
from core.world import WorldData, WorldDrawer
from puzzle.sudoku.handler import (ClearCellClickHandler,
                                   GenerateProblemClickHandler)


class SudokuWorldDrawer(WorldDrawer):
    def build(self, theme: Theme, root: WorldData):
        return LayerDrawer(
            children=[
                self.data.build(theme, root),
                LayerDrawer(
                    children=[
                        RectangleTextDrawer(
                            width=200, height=50,
                            text=text,
                            color=theme.color.primary,
                            text_color=theme.color.on_primary,
                            text_size=20,
                            on_click=[handler_cls(target=self.data)]
                        )
                        for text, handler_cls in self.button_list()
                    ],
                    gap=ConstantExcludeGapInfo(value=10, size=2),
                    direction=LayerDirection.COLUMN
                )
            ],
            gap=ConstantExcludeGapInfo(value=30, size=2),
            direction=LayerDirection.ROW
        )

    def button_list(self):
        yield "Generate Problem", GenerateProblemClickHandler
        yield "Clear", ClearCellClickHandler
