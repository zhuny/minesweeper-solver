import pygame.time
from pydantic import BaseModel

from core.drawer import CenteredRectangle
from core.theme import get_default_theme, Theme
from core.traveler import EventHandleTraveler


class WorldData(BaseModel):
    pass


class WorldSolver(BaseModel):
    pass


class WorldDrawer(BaseModel):
    data: WorldData
    solver: WorldSolver
    screen_size: tuple[int, int]

    def model_post_init(self, __context) -> None:
        self._screen = None
        self._node = None
        self._is_running = True
        self._is_draw_needed = True
        self._theme = get_default_theme()
        self._animation = []

    def build(self, theme: Theme, data: WorldData):
        raise NotImplementedError(type(self))

    def __enter__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(self.screen_size)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pygame.quit()

    def _init_node(self):
        s_width, s_height = self._screen.get_size()
        self._node = CenteredRectangle(
            child=self.build(self._theme, self.data),
            width=s_width, height=s_height
        )
        self._node.pos.set_xy(0, 0)

    def _handle_event(self):
        for e in pygame.event.get():
            match e.type:
                case pygame.QUIT:
                    self._is_running = False
                case pygame.MOUSEBUTTONUP:
                    if self._node.is_contained(e.pos):
                        self._animation.extend(
                            EventHandleTraveler(self._node, e.pos).visit()
                        )
                        self._is_draw_needed = True
                case pygame.KEYDOWN:
                    self._animation = []

    def _update(self):
        animation_list = []
        for animation in self._animation:
            for _ in animation:
                self._is_draw_needed = True
                animation_list.append(animation)
                break
        self._animation = animation_list

    def _draw_screen(self):
        if self._is_draw_needed:
            self._init_node()
            self._screen.fill(self._theme.color.background.as_tuple())
            self._node.draw(0, 0, self._screen)
            self._is_draw_needed = False
            pygame.display.flip()

    def main_loop(self):
        with self:
            self._init_node()

            clock = pygame.time.Clock()

            while self._is_running:
                self._handle_event()
                self._update()
                self._draw_screen()

                clock.tick(15)
