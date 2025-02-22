from typing import Any

from pydantic import BaseModel


class EventHandler(BaseModel):
    target: Any

    def handle(self):
        raise NotImplementedError(type(self))

    @staticmethod
    def wait(frame_number):
        for _ in range(frame_number):
            yield
