from dataclasses import dataclass
from pathlib import Path
from typing import List

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

    def set_save_place(self, x, y) -> bool:
        """
        :param x: 안전한 곳이라고 표시할 x위치
        :param y: 안전한 곳이라고 표시할 y위치
        :return: bool - 제대로 선택했는지에 대해서 확인
        """
        raise NotImplementedError


class MinesweeperWindowInterface(GameInterfaceBase):
    def __init__(self):
        super().__init__()

        self.is_loaded = False

        self.width = 30
        self.height = 16
        self.mine_count = 99
        self.place_info = [['-'] * self.width for _ in range(self.height)]
        self.block_info = list(self._load_block_info())
        self.is_game_over = False

    def _load_block_info(self):
        if not Path('mine_checker.png').exists():
            return

        canvas = Image.open('mine_checker.png')
        width, height = canvas.size
        width, height = width // 4, height // 4

        for i in range(16):
            if 5 <= i <= 8:
                continue

            y, x = divmod(i, 4)

            if i <= 8:
                t = str(i)
            elif i == 9:
                t = '!'
            elif i == 10:
                t = '-'
            else:
                continue

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
        index = None

        if result.isdigit():
            index = int(result)
        elif result == '!':
            index = 9
        elif result == '-':
            index = 10

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
        screenshot = ImageGrab.grab(rect, all_screens=True)

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

    def _iter_range(self):
        for x in range(self.width):
            for y in range(self.height):
                yield x, y

    def _load_screen_info(self):
        win32gui.EnumWindows(self._detect_game_rect, [])

    def _check_init(self):
        if not self.is_loaded:
            self._load_screen_info()

    def get_info(self) -> GameInfo:
        self._check_init()
        return GameInfo(
            mine_count=self.mine_count,
            width=self.width, height=self.height,
            mine_info=[''.join(row) for row in self.place_info],
            is_game_over=self.is_game_over
        )

    def set_save_place(self, x, y) -> bool:
        self._check_init()
        return True
