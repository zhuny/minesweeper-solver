import random
from typing import List, Tuple

from puzzle.game import GameInterfaceBase


class Relation:
    def __init__(self, pos_list, count):
        self.pos_list: List[Tuple[int, int]] = list(pos_list)
        self.pos_list.sort()
        self.count = count

    def is_subset(self, other):
        for i in self.pos_list:
            if i not in other.pos_list:
                return False
        return True

    def sub_info(self, other):
        return Relation(
            [
                pos
                for pos in other.pos_list
                if pos not in self.pos_list
            ],
            other.count - self.count
        )

    def is_empty(self):
        return len(self.pos_list) == 0

    def has_save(self):
        return len(self.pos_list) > 0 and self.count == 0

    def has_bomb(self):
        return len(self.pos_list) == self.count


class MinesweeperSolver:
    def __init__(self, api):
        self.api: GameInterfaceBase = api

    def solve(self):
        for i in range(100):
            self._solve_one()
            info = self.api.get_info()
            print('Solving Count', i)

            if info.is_game_over:
                break

    def _solve_one(self):
        info = self.api.get_info()

        relation_list = [
            Relation(self._adj_list(x, y, info), v)
            for x, y, v in self._number_block_list(info.mine_info)
        ]
        normalized: List[Relation] = []

        while relation_list:
            relation = relation_list.pop()
            if relation.is_empty():
                continue

            queue_size = len(relation_list)

            for norm in normalized:
                if norm.is_subset(relation):
                    relation_list.append(norm.sub_info(relation))
                elif relation.is_subset(norm):
                    relation_list.append(relation.sub_info(norm))
                    relation_list.append(relation)
                    normalized.remove(norm)
                else:
                    continue
                break

            if queue_size < len(relation_list):
                random.shuffle(relation_list)
            else:
                normalized.append(relation)

        clicked = 0
        bomb_set = set()

        for relation in normalized:
            if relation.has_save():
                for x, y in relation.pos_list:
                    self.api.set_save_place(x, y)
                clicked += len(relation.pos_list)
            elif relation.has_bomb():
                bomb_set.update(relation.pos_list)

        if clicked == 0:
            x, y = self._get_random_pos(info, bomb_set)
            self.api.set_save_place(x, y)

    def _get_random_pos(self, info, bomb_set):
        pos_list = [
            (x, y)
            for x in range(info.width)
            for y in range(info.height)
        ]
        random.shuffle(pos_list)

        for x, y in pos_list:
            if (x, y) in bomb_set:
                continue

            if info.mine_info[y][x] != '-':
                continue

            return x, y

    def _number_block_list(self, mine_info):
        for y, row in enumerate(mine_info):
            for x, v in enumerate(row):
                if v.isdigit():
                    v = int(v)
                    if 0 < v:
                        yield x, y, v

    def _adj_list(self, x, y, info):
        for x1 in range(x-1, x+2):
            for y1 in range(y-1, y+2):
                if x1 == x and y1 == y:
                    continue

                if 0 <= x1 < info.width:
                    if 0 <= y1 < info.height:
                        if info.mine_info[y1][x1] == '-':
                            yield x1, y1
