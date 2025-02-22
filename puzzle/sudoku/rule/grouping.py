class GroupSetting:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __hash__(self):
        return hash(type(self))

    def __eq__(self, other):
        return type(self) == type(other)

    def key(self, x, y):
        raise NotImplementedError(self)


class RowGroup(GroupSetting):
    def key(self, x, y):
        return x


class ColGroup(GroupSetting):
    def key(self, x, y):
        return y


class BoxGroup(GroupSetting):
    def key(self, x, y):
        return x // self.row, y // self.col
