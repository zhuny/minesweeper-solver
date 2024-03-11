import datetime
import functools
import re
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List

import win32api
import win32con
import win32gui
from PIL import Image, ImageChops, ImageGrab


@dataclass
class GameInfo:
    mine_count: int
    width: int
    height: int
    is_game_over: bool
    mine_info: List[str]


def average_color(histogram):
    total = 0
    color = 0
    for index, value in enumerate(histogram):
        total += value
        color += index * value

    return color / (total * 255)


def image_distance(img1, img2):
    assert img1.size == img2.size

    img_diff = ImageChops.difference(img1, img2)
    histogram = img_diff.histogram()
    avg_r = average_color(histogram[:256])
    avg_g = average_color(histogram[256:512])
    avg_b = average_color(histogram[512:])
    return (avg_r + avg_g + avg_b) / 3


class GameInterfaceBase:
    def get_info(self) -> GameInfo:
        raise NotImplementedError

    def set_safe_place(self, x, y):
        """
        :param x: 안전한 곳이라고 표시할 x위치
        :param y: 안전한 곳이라고 표시할 y위치
        :return: bool - 제대로 선택했는지에 대해서 확인
        """
        raise NotImplementedError

    def set_mine_place(self, x, y):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError


class LazyScreenshot:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.screenshot = None
        self.loaded = False

    def _check_loaded(self):
        if self.loaded:
            return

        rect = win32gui.GetWindowRect(self.hwnd)
        self.screenshot = ImageGrab.grab(rect, all_screens=True)
        self.loaded = True

    def crop(self, box):
        self._check_loaded()
        return self.screenshot.crop(box)


class MinesweeperWindowInterface(GameInterfaceBase):
    def __init__(self):
        super().__init__()

        self.is_loaded = False

        self.width = 30
        self.height = 16
        self.mine_count = 99
        self.place_info = [['-'] * self.width for _ in range(self.height)]
        self.is_game_over = False

        self.string_list = '012345xxx!->'

        self.block_info = list(self._load_block_info())

    def _load_block_info(self):
        if not Path('mine_checker.png').exists():
            return

        canvas = Image.open('mine_checker.png')
        width, height = canvas.size
        width, height = width // 4, height // 4

        for i, t in enumerate(self.string_list):
            if t == 'x':
                continue

            y, x = divmod(i, 4)

            yield canvas.crop(
                (
                    width * x, height * y,
                    width * (x + 1), height * (y + 1)
                )
            ), t

    def _is_game_title(self, name: str) -> bool:
        name = name.lower().strip()

        if not name.startswith('minesweeper'):
            return False

        if 'online' not in name:
            return False

        return True

    def _color_check(self, screenshot, box, color_map):
        subimage = screenshot.crop(box)

        color_map_check = [
            (image_distance(subimage, color), value)
            for color, value in color_map
        ]
        return min(color_map_check)[1]

    def _save_info(self, screenshot, box, result: str):
        index = self.string_list.find(result)

        assert 0 <= index

        y, x = divmod(index, 4)

        subimage = screenshot.crop(box)
        w, h = subimage.size

        if not Path('mine_checker.png').exists():
            Image.new('RGB', (w * 4, h * 4)).save('mine_checker.png')

        canvas = Image.open('mine_checker.png')
        canvas.paste(subimage, (w * x, h * y))
        canvas.save('mine_checker.png')

    def _detect_game_rect(self, hwnd, result):
        # 열려있는지 확인
        if not win32gui.IsWindowVisible(hwnd):
            return

        # Game 화면인지 확인
        title: str = win32gui.GetWindowText(hwnd)
        if not self._is_game_title(title):
            return

        # 스크린샷 찍기
        rect = win32gui.GetWindowRect(hwnd)
        screenshot = LazyScreenshot(hwnd)

        # callback 실행하기
        for callback in result:
            callback(rect, screenshot)

    def _load_game_info(self, rect, screenshot):
        middle = (rect[2] - rect[0]) // 2

        # 게임오버 되었는지 확인하기
        square = 15
        size = square * 2, square * 2
        self.is_game_over = self._color_check(
            screenshot,
            (middle - square, 200 - square, middle + square, 200 + square),
            [
                (Image.new('RGB', size, (255, 0, 0)), True),
                (Image.new('RGB', size, (0, 255, 0)), False)
            ]
        )

        mine = 25
        offset_x = self.width * mine // 2
        offset_y = 240
        padding = 0

        for x, y in self._iter_range():
            left = middle - offset_x + x * mine
            top = offset_y + y * mine

            result = self._color_check(
                screenshot,
                (
                    left + padding, top + padding,
                    left + mine - padding, top + mine - padding
                ),
                self.block_info
            )
            self.place_info[y][x] = result

    def _save_digit_num(self, rect, screenshot):
        middle = (rect[2] - rect[0]) // 2

        mine = 25
        offset_x = self.width * mine // 2
        offset_y = 240
        padding = 0

        temp_number_info = {
            (0, 0): '>'
        }
        for (x, y), v in temp_number_info.items():
            left = middle - offset_x + x * mine
            top = offset_y + y * mine

            self._save_info(
                screenshot,
                (
                    left + padding, top + padding,
                    left + mine - padding, top + mine - padding
                ),
                v
            )

    def _iter_range(self):
        for x in range(self.width):
            for y in range(self.height):
                yield x, y

    def _load_screen_info(self):
        win32gui.EnumWindows(self._detect_game_rect, [self._load_game_info])

    def _check_init(self):
        if not self.is_loaded:
            self._load_screen_info()
            self.is_loaded = True

    def get_info(self) -> GameInfo:
        self._check_init()
        return GameInfo(
            mine_count=self.mine_count,
            width=self.width, height=self.height,
            mine_info=[''.join(row) for row in self.place_info],
            is_game_over=self.is_game_over
        )

    def _click_save_place(self, x, y, down, up, rect, screenshot):
        middle = (rect[2] - rect[0]) // 2
        mine = 25
        offset_x = self.width * mine // 2
        offset_y = 240

        left = rect[0] + middle - offset_x + x * mine + mine // 2
        top = rect[1] + offset_y + y * mine + mine // 2

        win32api.SetCursorPos((left, top))
        win32api.mouse_event(down, left, top, 0, 0)
        win32api.mouse_event(up, left, top, 0, 0)
        time.sleep(0.5)

    def set_safe_place(self, x, y) -> bool:
        print('Save Place :', x, y)
        self.is_loaded = False
        win32gui.EnumWindows(
            self._detect_game_rect,
            [functools.partial(
                self._click_save_place,
                x, y,
                win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP
            )]
        )
        return True

    def save_digit(self):
        win32gui.EnumWindows(self._detect_game_rect, [self._save_digit_num])

    def set_mine_place(self, x, y):
        print('Dangerous Place :', x, y)
        win32gui.EnumWindows(
            self._detect_game_rect,
            [functools.partial(
                self._click_save_place,
                x, y,
                win32con.MOUSEEVENTF_RIGHTDOWN, win32con.MOUSEEVENTF_RIGHTUP
            )]
        )

    def _reset_game(self, rect, screenshot):
        middle = (rect[2] + rect[0]) // 2
        top = rect[1] + 200
        win32api.SetCursorPos((middle, top))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, middle, top, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, middle, top, 0, 0)
        time.sleep(0.5)

    def reset(self):
        win32gui.EnumWindows(
            self._detect_game_rect,
            [self._reset_game]
        )
