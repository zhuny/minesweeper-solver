from core.drawer import (ConstantExcludeGapInfo, LayerDirection, LayerDrawer,
                         RectangleTextDrawer)
from core.theme import Theme
from core.world import WorldDrawer


class SudokuWorldDrawer(WorldDrawer):
    def build(self, theme: Theme):
        return LayerDrawer(
            children=[
                self.data.build(theme),
                LayerDrawer(
                    children=[
                        RectangleTextDrawer(
                            width=200, height=50,
                            text="Generate Problem",
                            color=theme.color.primary,
                            text_color=theme.color.on_primary,
                            text_size=20
                        )
                    ],
                    gap=ConstantExcludeGapInfo(value=10, size=1),
                    direction=LayerDirection.COLUMN
                )
            ],
            gap=ConstantExcludeGapInfo(value=30, size=2),
            direction=LayerDirection.ROW
        )
