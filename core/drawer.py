import collections
import enum

import pygame.draw
from pydantic import BaseModel, Field

from core.theme import MyColor


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

    def offset_rect(self, x, y):
        return GeometryInfo(
            x=self.x + x, y=self.y + y,
            w=self.w, h=self.h
        )

    def is_contained(self, x, y):
        return (
            self.x <= x < self.x + self.w and
            self.y <= y < self.y + self.h
        )

    def rel_pos(self, x, y):
        return x - self.x, y - self.y

    def as_tuple(self):
        return self.x, self.y, self.w, self.h


class DrawerBase(BaseModel):
    pos: GeometryInfo = Field(default_factory=GeometryInfo)
    color: MyColor = None

    @property
    def cls_name(self):
        return type(self).__name__

    def model_post_init(self, __context) -> None:
        """
        Use this function to initialize GeometryInfo
        현재 node는 w, h를 정의해야 하며
        parent는 child의 x, y를 정의해 주어야 한다.
        """
        raise NotImplementedError(type(self))

    def draw(self, offset_x, offset_y, screen):
        raise NotImplementedError(type(self))

    def is_contained(self, pos):
        return self.pos.is_contained(pos[0], pos[1])

    def rel_pos(self, pos):
        return self.pos.rel_pos(pos[0], pos[1])


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
    gap: TableGapInfo

    def model_post_init(self, __context) -> None:
        row_width_list = []
        col_width_list = []

        for child in self.children:
            row_width_list.append(child.pos.w)
            col_width_list.append(child.pos.h)

        match self.direction:
            case LayerDirection.ROW:
                row_pos_list = self.gap.build_pos(row_width_list)
                for pos, child in zip(row_pos_list, self.children):
                    child.pos.x = pos
                    child.pos.y = 0
                self.pos.w = row_pos_list[-1]
                self.pos.h = max(col_width_list)

            case LayerDirection.COLUMN:
                col_pos_list = self.gap.build_pos(col_width_list)
                for pos, child in zip(col_pos_list, self.children):
                    child.pos.x = 0
                    child.pos.y = pos
                self.pos.w = max(row_width_list)
                self.pos.h = col_pos_list[-1]

    def draw(self, offset_x, offset_y, screen):
        offset_x += self.pos.x
        offset_y += self.pos.y

        for child in self.children:
            child.draw(offset_x, offset_y, screen)


class RectangleDrawer(DrawerBase):
    width: int
    height: int

    def model_post_init(self, __context) -> None:
        self.pos.w = self.width
        self.pos.h = self.height

    def draw(self, offset_x, offset_y, screen):
        pygame.draw.rect(
            screen, self.color.as_tuple(),
            self.pos.offset_rect(offset_x, offset_y).as_tuple()
        )


class RectangleTextDrawer(RectangleDrawer):
    text: str
    text_size: int
    text_color: MyColor

    def draw(self, offset_x, offset_y, screen):
        super().draw(offset_x, offset_y, screen)

        from core.draw_it import FontDrawer, blit_center

        surface = FontDrawer.render_text(
            self.text, self.text_size,
            self.text_color
        )
        blit_center(
            screen, surface,
            self.pos.offset_rect(offset_x, offset_y)
        )


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

    def draw(self, offset_x, offset_y, screen):
        pygame.draw.rect(
            screen, self.color.as_tuple(),
            self.pos.offset_rect(offset_x, offset_y).as_tuple()
        )

        offset_x += self.pos.x
        offset_y += self.pos.y

        for cell in self.cell_list:
            cell.drawer.draw(offset_x, offset_y, screen)
