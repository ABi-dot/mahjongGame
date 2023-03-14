from utils.rule import Rule


class Expose(object):
    __slots__ = ("_outer", "_outer_owner_position", "_inners", "_all", 'expose_type')

    def __init__(self, expose_type: str, inners: list, outer=None, outer_owner_position=None):
        self.expose_type = expose_type
        self._inners = inners
        self._outer = outer
        self._outer_owner_position = outer_owner_position
        self._all: list = self._inners[:]
        if outer:
            self._all.append(outer)
            Rule.sort(self._all)

    def __str__(self):
        _str = ','.join([f'{x}' for x in self._inners])
        if self._outer:
            _str += f",{self._outer}"
            if self._outer_owner_position:
                _str += f"({self._outer_owner_position})"
        return _str

    @property
    def inners(self):
        return self._inners

    @property
    def outer(self):
        return self._outer

    @property
    def outer_owner_position(self):
        return self._outer_owner_position

    @property
    def all(self):
        return self._all
