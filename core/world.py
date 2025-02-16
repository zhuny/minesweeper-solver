import pygame.time
from pydantic import BaseModel


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

    def _build(self):
        raise NotImplementedError(type(self))

    def __enter__(self):
        pygame.init()
        # self._screen = pygame.display.set_mode((1920, 1080))

    def __exit__(self, exc_type, exc_val, exc_tb):
        pygame.quit()

    def main_loop(self):
        with self:
            clock = pygame.time.Clock()
            self.node = self._build()

            while self._is_running:
                self._handle_event()
                self._update_data()
                self._draw_screen()

                clock.tick(15)
