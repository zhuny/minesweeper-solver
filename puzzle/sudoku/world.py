from core.drawer import (LayerDirection, LayerDrawer,
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
                    gap=10,
                    direction=LayerDirection.COLUMN
                )
            ],
            gap=10,
            direction=LayerDirection.ROW
        )
