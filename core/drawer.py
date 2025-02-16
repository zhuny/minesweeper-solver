import enum

from pydantic import BaseModel, Field


class GeometryInfo(BaseModel):
    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None


class DrawerBase(BaseModel):
    pos: GeometryInfo = Field(default_factory=GeometryInfo)

    def model_post_init(self, __context) -> None:
        """
        Use this function to initialize GeometryInfo
        """
        raise NotImplementedError(type(self))


class LayerDirection(enum.Enum):
    ROW = 1
    COLUMN = 2


class LayerDrawer(DrawerBase):
    children: list[DrawerBase]
    direction: LayerDirection
    gap: int


class RectangleDrawer(DrawerBase):
    width: int
    height: int

    def model_post_init(self, __context) -> None:
        self.pos.w = self.width
        self.pos.h = self.height


class ButtonDrawer(RectangleDrawer):
    text: str


class TableGapInfo(BaseModel):
    def size_check(self, size: int) -> bool:
        raise NotImplementedError(type(self))


class ConstantGapInfo(TableGapInfo):
    """
    일정한 gap을 갖는 경우
    """
    value: int

    def size_check(self, size: int) -> bool:
        return True


class GapListInfo(TableGapInfo):
    """
    각 gap마다 사이즈가 다른 경우
    """
    value: list[int]

    def size_check(self, size: int) -> bool:
        return len(self.value) == size + 1


class TableDrawer(DrawerBase):
    cell_list: list[DrawerBase]
    row_gap: TableGapInfo
    col_gap: TableGapInfo
    cell_width: int
    cell_height: int
