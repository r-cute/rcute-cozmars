from . import util

class Infrared(util.Component):
    """Infrared Sensor
    """
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_state_changed = None
        """Callback function, called when the value of any infrared sensor at the bottom changes, the default is `None`

        The callback function accepts one parameter, which is a `tuple` composed of the values of two infrared sensors"""
        self._state = (1, 1)

    @property
    def state(self):
        """ A two-element `tuple` composed of the infrared sensor values, each element is `0` or `1`

        `1` means reflection is received, `0` means no reflection is received """
        return self._state
