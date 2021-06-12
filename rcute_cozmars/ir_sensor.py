from . import util
from . import pair
import weakref

class IRSensor(pair.Child):
    def __init__(self, i, p):
        pair.Child.__init__(self, i, total=3)
        self._parent_ref = weakref.ref(p)

    @property
    def state(self):
        return self.extract(self._parent_ref().state)


class IRSensors(util.Component, pair.Parent):
    """Infrared Sensors at the bottom
    """
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        pair.Parent.__init__(self, IRSensor, self, len=3)
        self.when_state_changed = None
        """Callback function, called when the value of any infrared sensor at the bottom changes, the default is `None`

        The callback function accepts one parameter, which is a `tuple` composed of the values of two infrared sensors"""
        self._state = [1,1,1]

    @property
    def state(self):
        """ A two-element `tuple` composed of the infrared sensor values, each element is `0` or `1`

        `1` means reflection is received, `0` means no reflection is received """
        return tuple(self._state)
