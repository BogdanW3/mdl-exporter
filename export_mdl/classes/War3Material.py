from typing import List

from .War3Layer import War3Layer


class War3Material:
    def __init__(self, name):
        self.name: str = name
        self.layers: List[War3Layer] = []
        self.use_const_color: bool = False
        self.priority_plane: int = 0
        self.is_hd: bool = False

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # return hash(tuple(sorted(self.__dict__.items())))
        return hash(self.name)

    def write_mdl(self, fw):
        pass
