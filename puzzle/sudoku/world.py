from core.drawer import ButtonDrawer, LayerDirection, LayerDrawer
from core.world import WorldDrawer


class SudokuWorldDrawer(WorldDrawer):
    def _build(self):
        return LayerDrawer(
            children=[
                self.data._build(),
                LayerDrawer(
                    ButtonDrawer
                )
            ],
            gap=10,
            direction=LayerDirection.ROW
        )
