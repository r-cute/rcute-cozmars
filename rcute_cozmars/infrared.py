from . import error, util

class Infrared(util.Component):
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_changed = None
        self._state = (1, 1)

    @property
    def state(self):
        return self._state


