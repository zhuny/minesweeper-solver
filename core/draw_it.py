import pygame.font

from core.drawer import GeometryInfo
from core.theme import MyColor


class FontDrawer:
    font_file = (
        'C:/Users/zhuny/PycharmProjects/video-editor/NanumSquareNeo-eHv.ttf'
    )
    font_obj_map = {}

    @classmethod
    def render_text(cls, text, size, color: MyColor):
        renderer = cls._get_font_obj(size)
        return renderer.render(text, True, color.as_tuple())

    @classmethod
    def _get_font_obj(cls, size):
        if size not in cls.font_obj_map:
            font_obj = pygame.font.Font(cls.font_file, size)
            cls.font_obj_map[size] = font_obj
            return font_obj
        else:
            return cls.font_obj_map[size]


def blit_center(screen: pygame.Surface,
                surface: pygame.Surface,
                pos: GeometryInfo):
    left = pos.x + (pos.w - surface.get_width()) // 2
    top = pos.y + (pos.h - surface.get_height()) // 2
    screen.blit(surface, (left, top))
