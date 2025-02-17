import functools
import re
from typing import Any

from pydantic import BaseModel, model_validator

"""
Reference for color and variety values
https://m2.material.io/design/color/dark-theme.html
"""


class MyColor(BaseModel):
    r: int
    g: int
    b: int

    def as_tuple(self):
        return self.r, self.g, self.b

    @model_validator(mode='before')
    @classmethod
    def wrap_many_represent(cls, data: Any) -> Any:
        if isinstance(data, str):
            if g1 := cls._color_hex_rex().fullmatch(data):
                data = [int(v, 16) for v in g1.groups()]
            else:
                raise ValueError('Not formatted str value')

        if isinstance(data, (list, tuple)):
            if len(data) != 3:
                raise ValueError('Unknown color info')
            data = dict(zip('rgb', data))

        if not isinstance(data, dict):
            raise ValueError('Unknown type')

        return data

    @functools.cache
    @staticmethod
    def _color_hex_rex():
        hex_re = r'[0-9a-fA-F]'
        one_color_re = f'({hex_re}{hex_re})'
        whole_color_re = '#' + one_color_re * 3
        return re.compile(whole_color_re)


class ThemeColor(BaseModel):
    primary: MyColor
    secondary: MyColor
    background: MyColor
    surface: MyColor
    error: MyColor

    primary_variant: MyColor
    secondary_variant: MyColor

    on_primary: MyColor
    on_secondary: MyColor
    on_background: MyColor
    on_surface: MyColor
    on_error: MyColor


class Theme(BaseModel):
    color: ThemeColor


def get_default_theme():
    return Theme(
        color=ThemeColor(
            primary="#6200EE",
            secondary="#03DAC6",
            background="#FFFFFF",
            surface="#FFFFFF",
            error="#B00020",
            primary_variant="#3700B3",
            secondary_variant="#018786",
            on_primary="#FFFFFF",
            on_secondary="#000000",
            on_background="#000000",
            on_surface="#000000",
            on_error="#FFFFFF"
        )
    )
