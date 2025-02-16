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

    def build(self):
        raise NotImplementedError(type(self))

    def __enter__(self):
        pygame.init()
        self._screen = pygame.display.set_mode((1920, 1080))

    def __exit__(self, exc_type, exc_val, exc_tb):
        pygame.quit()

    def _handle_event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self._is_running = False

    def _update_data(self):
        pass

    def _draw_screen(self):
        pass

    def main_loop(self):
        with self:
            clock = pygame.time.Clock()
            self._node = self.build()

            while self._is_running:
                self._handle_event()
                self._update_data()
                self._draw_screen()

                clock.tick(15)
