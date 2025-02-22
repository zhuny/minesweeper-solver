from core.drawer import (ConstantExcludeGapInfo, LayerDirection, LayerDrawer,
                         RectangleTextDrawer)
from core.theme import Theme
from core.world import WorldData, WorldDrawer
from puzzle.sudoku.handler import (AutoGenerateClickHandler,
                                   ClearCellClickHandler,
                                   CompleteProblemClickHandler,
                                   GenerateProblemClickHandler,
                                   SolveUniqueClickHandler)


class SudokuWorldDrawer(WorldDrawer):
    def build(self, theme: Theme, root: WorldData):
        return LayerDrawer(
            children=[
                self.data.build(theme, root),
                LayerDrawer(
                    children=list(self.button_list(theme)),
                    gap=ConstantExcludeGapInfo(value=10, size=6),
                    direction=LayerDirection.COLUMN
                )
            ],
            gap=ConstantExcludeGapInfo(value=30, size=2),
            direction=LayerDirection.ROW
        )

    def button_text_list(self):
        yield "Generate Problem", GenerateProblemClickHandler
        yield "Solve and Unique", SolveUniqueClickHandler
        yield "Clear", ClearCellClickHandler
        yield "Auto", AutoGenerateClickHandler
        yield "Complete", CompleteProblemClickHandler
        yield self.data.message, None

    def button_list(self, theme):
        for text, handler_cls in self.button_text_list():
            yield RectangleTextDrawer(
                width=220, height=50,
                text=text,
                color=(
                    theme.color.secondary
                    if handler_cls is None else
                    theme.color.primary
                ),
                text_color=(
                    theme.color.on_secondary
                    if handler_cls is None else
                    theme.color.on_primary
                ),
                text_size=20,
                on_click=(
                    [handler_cls(target=self.data)]
                    if handler_cls is not None else []
                )
            )
