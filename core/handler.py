from typing import Any

from pydantic import BaseModel


class EventHandler(BaseModel):
    target: Any

    def handle(self):
        raise NotImplementedError(type(self))
