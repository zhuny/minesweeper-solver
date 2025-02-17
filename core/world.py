import pygame.time
from pydantic import BaseModel

from core.theme import get_default_theme, Theme


class WorldData(BaseModel):
    pass


class WorldSolver(BaseModel):
    pass


class WorldDrawer(BaseModel):
    data: WorldData
    solver: WorldSolver

    def model_post_init(self, __context) -> None:
        self._screen = None
        self._node = None
        self._is_running = True
        self._is_draw_needed = True
        self._theme = get_default_theme()

    def build(self, theme: Theme):
        raise NotImplementedError(type(self))

    def __enter__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((1920, 1080))

    def __exit__(self, exc_type, exc_val, exc_tb):
        pygame.quit()

    def _init_node(self):
        self._node = self.build(self._theme)

        s_width, s_height = self._screen.get_size()
        self._node.pos.x = (s_width - self._node.pos.w) // 2
        self._node.pos.y = (s_height - self._node.pos.h) // 2

    def _handle_event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self._is_running = False

    def _update_data(self):
        pass

    def _draw_screen(self):
        if self._is_draw_needed:
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
                self._update_data()
                self._draw_screen()

                clock.tick(15)
