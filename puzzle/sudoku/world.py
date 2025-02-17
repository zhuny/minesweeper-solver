from core.drawer import (ConstantExcludeGapInfo, LayerDirection, LayerDrawer,
                         RectangleTextDrawer)
from core.world import WorldDrawer


class SudokuWorldDrawer(WorldDrawer):
    def build(self):
        return LayerDrawer(
            children=[
                self.data.build(),
                LayerDrawer(
                    children=[
                        RectangleTextDrawer(
                            width=200, height=50,
                            text="Generate Problem"
                        )
                    ],
                    gap=ConstantExcludeGapInfo(value=10, size=1),
                    direction=LayerDirection.COLUMN
                )
            ],
            gap=ConstantExcludeGapInfo(value=30, size=2),
            direction=LayerDirection.ROW
        )
