import collections
import enum

from pydantic import BaseModel, Field


class TableGapInfo(BaseModel):
    def size_check(self, size: int) -> bool:
        raise NotImplementedError(type(self))

    def get(self, index: int) -> int:
        raise NotImplementedError(type(self))

    def build_pos(self, size_list: list[int]):
        pos_result = [self.get(0)]
        for index, width in enumerate(size_list, 1):
            pos_result.append(pos_result[-1] + width + self.get(index))
        return pos_result


class ConstantGapInfo(TableGapInfo):
    """
    일정한 gap을 갖는 경우
    """
    value: int

    def size_check(self, size: int) -> bool:
        return True

    def get(self, index: int) -> int:
        return self.value


class ConstantExcludeGapInfo(TableGapInfo):
    """
    양 끝을 제외하고 gap이 constant인 경우
    """
    value: int
    size: int

    def size_check(self, size: int) -> bool:
        return self.size + 1 == size

    def get(self, index: int) -> int:
        if index == 0 or index == self.size:
            return 0
        else:
            return self.value


class GapListInfo(TableGapInfo):
    """
    각 gap마다 사이즈가 다른 경우
    """
    value: list[int]

    def size_check(self, size: int) -> bool:
        return len(self.value) == size + 1

    def get(self, index: int) -> int:
        return self.value[index]


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


class MaxSumProcess:
    def __init__(self):
        self.max_value = 0
        self.sum_value = 0

    def update(self, value):
        self.max_value = max(self.max_value, value)
        self.sum_value += value


class LayerDrawer(DrawerBase):
    children: list[DrawerBase]
    direction: LayerDirection
    gap: int

    def model_post_init(self, __context) -> None:
        row_pos_list = []
        col_pos_list = []

        for child in self.children:
            row_pos_list.append(child.pos.w)
            col_pos_list.append(child.pos.h)

        match self.direction:
            case LayerDirection.ROW:
                self.pos.x


class RectangleDrawer(DrawerBase):
    width: int
    height: int

    def model_post_init(self, __context) -> None:
        self.pos.w = self.width
        self.pos.h = self.height


class RectangleTextDrawer(RectangleDrawer):
    text: str


class MaxContainer(collections.defaultdict):
    def __init__(self):
        super().__init__(int)

    def update_value(self, key, value):
        self[key] = max(self[key], value)

    def get_sorted_items(self):
        return sorted(self.items())


class TableCellInfo(BaseModel):
    x: int
    y: int
    drawer: DrawerBase


class TableDrawer(DrawerBase):
    # TODO: 아직 merge에 대해서는 고려하지 말자
    cell_list: list[TableCellInfo]

    # TODO: DO field validation
    row_gap: TableGapInfo
    col_gap: TableGapInfo
    cell_width: int
    cell_height: int

    def model_post_init(self, __context) -> None:
        # 각 column, row 별로 크기 계산
        row_size_container = MaxContainer()
        col_size_container = MaxContainer()

        for cell in self.cell_list:
            row_size_container.update_value(cell.x, cell.drawer.pos.w)
            col_size_container.update_value(cell.y, cell.drawer.pos.h)

        row_pos_list = self.row_gap.build_pos([
            row_size_container[i]
            for i in range(self.cell_width)
        ])
        col_pos_list = self.col_gap.build_pos([
            col_size_container[i]
            for i in range(self.cell_height)
        ])

        # 각 cell마다 적용
        for cell in self.cell_list:
            cell.drawer.pos.x = row_pos_list[cell.x]
            cell.drawer.pos.y = col_pos_list[cell.y]

        self.pos.w = row_pos_list[-1]
        self.pos.h = col_pos_list[-1]
