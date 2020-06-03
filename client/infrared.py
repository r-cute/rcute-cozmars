from . import error, util

class Infrared(util.Component):
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.value_changed = None
        self._value = False

    @property
    def value(self):
        return self._value


