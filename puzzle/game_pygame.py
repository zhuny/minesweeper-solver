import random

import pygame

from puzzle.game import GameInfo, GameInterfaceBase


class PygameCanvas:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1600, 900))
        self.font = pygame.font.Font(
            pygame.font.get_default_font(),
            24
        )
        self.clock = pygame.time.Clock()
        self.check_image = pygame.transform.smoothscale(
            pygame.image.load('check.png'),
            (28, 28)
        )

    def __del__(self):
        pygame.quit()

    def wait(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return
            pygame.display.flip()
            self.clock.tick(10)

    def _get_subsurface_info(self, info):
        gap = 4
        size = 32

        total_width = gap * 2 + size * info.width
        total_height = gap * 3 + size * (info.height + 1)

        screen_width, screen_height = self.screen.get_size()
        offset_width = (screen_width - total_width) // 2
        offset_height = (screen_height - total_height) // 2

        return {
            'size': self._fill_and_get_subsurface([
                offset_width + gap, offset_height + gap,
                size * 6, size
            ], gap),
            'place': self._fill_and_get_subsurface([
                offset_width + gap, offset_height + gap * 2 + size,
                size * info.width, size * info.height
            ], gap)
        }

    def _fill_and_get_subsurface(self, box, gap):
        outer_box = [box[0]-gap, box[1]-gap, box[2] + gap*2, box[3] + gap*2]
        self.screen.fill((64, 64, 64), outer_box)
        self.screen.fill('black', box)
        return self.screen.subsurface(box)

    def draw(self, info: GameInfo):
        self.screen.fill('black')

        subsurfaces = self._get_subsurface_info(info)

        size = 32

        self._draw_info(subsurfaces['size'], info)

        for j, row in enumerate(info.mine_info):
            for i, cell in enumerate(row):
                self._draw_cell(subsurfaces['place'], i, j, cell, size)

        pygame.event.get()
        pygame.display.flip()
        if info.is_game_over:
            self.clock.tick(1)
        else:
            self.clock.tick(15)

    _number_to_color = {
        '1': (255, 255, 0),
        '2': (255, 0, 255),
        '3': (0, 255, 255),
        '4': (255, 0, 0),
        '5': (0, 255, 0),
        '6': (0, 0, 255),
        '7': (127, 127, 127),
        '8': (127, 127, 127)
    }

    def _draw_cell(self, screen, x, y, cell, size):
        if cell == '-':
            return

        this_box = [x * size, y * size, size, size]

        if cell.isdigit():
            screen.fill((64, 64, 64), this_box)
            if 1 <= int(cell):
                text_surface = self.font.render(
                    cell, True,
                    self._number_to_color[cell]
                )
                self._blit_center(screen, text_surface, this_box)
        elif cell == '>':
            self._blit_center(screen, self.check_image, this_box)
        elif cell == '!':
            pygame.draw.circle(
                screen,
                'red',
                pygame.Rect(this_box).center,
                size * 2 / 5
            )

    def _draw_info(self, screen, info):
        text_surface = self.font.render(
            f'{info.width} x {info.height} ({info.mine_count})',
            True,
            (223, 223, 223)
        )
        self._blit_center(
            screen,
            text_surface,
            [4, 0, screen.get_width()-4, screen.get_height()],
            left='first'
        )

    def _blit_center(self,
                     screen, surface, box,
                     *, left='middle', top='middle'):
        if box is None:
            box = screen.get_rect()

        x = self._get_align(box[0], box[2], surface.get_width(), left)
        y = self._get_align(box[1], box[3], surface.get_height(), top)
        screen.blit(surface, (x, y))

    def _get_align(self, main_pos, main_width, sub_width, align):
        if align == 'first':
            return main_pos
        elif align == 'middle':
            return main_pos + (main_width - sub_width) // 2
        elif align == 'last':
            return main_pos + main_width - sub_width


class PygameInterface(GameInterfaceBase):
    def __init__(self, width, height, mine_count):
        self.width = width
        self.height = height
        self.mine_count = mine_count

        self.mine_position = set()

        self.mine_info = [
            ['-'] * width
            for _ in range(height)
        ]
        self.is_init = False
        self.is_game_over = False
        self.is_good = False

        self.canvas = PygameCanvas()

        self.reset()

    def get_info(self) -> GameInfo:
        return GameInfo(
            mine_count=self.mine_count,
            width=self.width,
            height=self.height,
            is_game_over=self.is_game_over,
            mine_info=[''.join(row) for row in self.mine_info]
        )

    def set_safe_place(self, x, y):
        if self.is_game_over:
            return

        print('Safe', x, y)
        if not self.is_init:
            # 첫번째 클릭에서는 무조건 지뢰가 나오지 않도록 한다.
            self._init_mine_position(x, y)

        if (x, y) in self.mine_position:
            self.is_game_over = True
            self.is_good = False
            self.mine_info[y][x] = '!'
            self._draw()
            return

        # 연쇄적으로 열리는 것 구현
        click_count = 0
        queue = [(x, y)]
        while queue:
            xx, yy = queue.pop()
            if self.mine_info[yy][xx] != '-':
                continue

            count = self._get_adj_mine(xx, yy)
            self.mine_info[yy][xx] = str(count)
            click_count += 1
            if count == 0:
                queue.extend(self._get_adj_list(xx, yy))

        # 다 잘 눌렀는지 확인
        if click_count > 0:
            self._check_is_over()

    def _check_is_over(self):
        total = ''.join(
            cell
            for row in self.mine_info for cell in row
        )
        self.is_game_over = '-' not in total
        if self.is_game_over:
            self.is_good = (
                total.count('>') == self.mine_count and
                all(
                    self.mine_info[y][x] == '>'
                    for x, y in self.mine_position
                )
            )
        # self._show_info()
        self._draw()

    def _get_adj_mine(self, x, y):
        return len([
            pos
            for pos in self._get_adj_list(x, y)
            if pos in self.mine_position
        ])

    def _get_adj_list(self, x, y):
        for xx in range(x-1, x+2):
            for yy in range(y-1, y+2):
                if xx == x and yy == y:
                    continue

                if 0 <= xx < self.width:
                    if 0 <= yy < self.height:
                        yield xx, yy

    def _init_mine_position(self, x, y):
        position_list = [
            (i, j)
            for i in range(self.width)
            for j in range(self.height)
            if not (i == x and j == y)
        ]
        random.shuffle(position_list)
        self.mine_position = set(position_list[:self.mine_count])
        self.is_init = True

    def _show_info(self):
        print(self.is_game_over, self.is_good)
        for y, row in enumerate(self.mine_info):
            cell_list = []
            for x, cell in enumerate(row):
                if (x, y) in self.mine_position:
                    cell += '!'
                else:
                    cell += ' '
                cell_list.append(cell)
            print(''.join(cell_list))
        input()

    def set_mine_place(self, x, y):
        if self.mine_info[y][x] == '-':
            self.mine_info[y][x] = '>'
            print('Mine', x, y)
            self._check_is_over()

    def reset(self):
        self.mine_position = set()
        self.mine_info = [
            ['-'] * self.width
            for _ in range(self.height)
        ]
        self.is_init = False
        self.is_game_over = False
        self.is_good = False
        self._draw()

    def _draw(self):
        self.canvas.draw(self.get_info())

    def wait(self):
        self.canvas.wait()
