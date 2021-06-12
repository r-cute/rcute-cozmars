from collections import Iterable

class Child:
    def __init__(self, i, total=2):
        self._index = i
        self._total = total

    def extend(self, v):
        r = [None] * self._total
        r[self._index] = v
        return tuple(r)

    def extract(self, v):
        return v[self._index]

class Parent:
    def __init__(self, child_class, *args, len=2):
        self._children = tuple(child_class(i, *args) for i in range(len))

    def extend(self, v):
        l = len(self._children)
        return v if isinstance(v, Iterable) and len(v)==l else (v,) *l

    def extract(self, v):
        return v

    _index_map = {'left':0, 'right':-1, 'middle':1}
    def __getitem__(self, i):
        return self._children[Parent._index_map.get(i, i)]
