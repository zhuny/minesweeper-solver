from core.drawer import DrawerBase, TableCellInfo


class Traveler:
    debug = False

    def __init__(self, drawable: DrawerBase):
        self.drawable = drawable

    def visit(self):
        stack = [(True, self.drawable)]

        while stack:
            is_push, drawable = stack.pop()

            if is_push:
                children = [
                    (True, child)
                    for child in self.get_children(drawable)
                ]
                children.append((False, drawable))
                children.reverse()
                stack.extend(children)

                getattr(
                    self, f'push_drawable_{drawable.cls_name}',
                    self.push_drawable
                )(drawable)

            else:
                getattr(
                    self, f'pop_drawable_{drawable.cls_name}',
                    self.pop_drawable
                )(drawable)

    def get_children(self, drawable: DrawerBase):
        return self._travel_model(drawable, drawable)

    def _travel_model(self, obj, root):
        if isinstance(obj, DrawerBase):
            if obj is root:
                for name in obj.model_fields:
                    yield from self._travel_model(getattr(obj, name), root)
            else:
                yield obj
        elif isinstance(obj, TableCellInfo):
            yield obj.drawer
        elif isinstance(obj, (list, tuple, dict)):
            if isinstance(obj, dict):
                obj = obj.values()
            for e in obj:
                yield from self._travel_model(e, root)

    def push_drawable(self, drawable: DrawerBase):
        if self.debug:
            print('Push', drawable.cls_name, drawable.pos)

    def pop_drawable(self, drawable: DrawerBase):
        if self.debug:
            print('Pop', drawable.cls_name, drawable.pos)


class EventHandleTraveler(Traveler):
    debug = False

    def __init__(self, drawable: DrawerBase, pos):
        super().__init__(drawable)
        self.pos = pos
        self.pos_stack = [pos]

    def top_pos(self):
        return self.pos_stack[-1]

    def get_children(self, drawable: DrawerBase):
        pos = drawable.rel_pos(self.top_pos())
        for child in super().get_children(drawable):
            if child.is_contained(pos):
                yield child

    def push_drawable(self, drawable: DrawerBase):
        super().push_drawable(drawable)
        self.pos_stack.append(drawable.rel_pos(self.top_pos()))

    def pop_drawable(self, drawable: DrawerBase):
        self.pos_stack.pop()
        super().pop_drawable(drawable)
