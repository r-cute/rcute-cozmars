from collections import Iterable

class Child:
    def __init__(self, i):
        self._index = i

    def extend(self, v):
        return (None, v) if self._index else (v, None)

    def extract(self, v):
        return v[self._index]

class Parent:
    def __init__(self, child_class, *args):
        self._children = (child_class(0, *args), child_class(1, *args))

    def extend(self, v):
        return v if isinstance(v, Iterable) and len(v)==2 else v

    def extract(self, v):
        return v

    def __getitem__(self, i):
        if i == 'left':
            i = 0
        elif i == 'right':
            i = 1
        return self._children[i]
