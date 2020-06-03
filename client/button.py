from .util import mode, Component
from . import error

class Button(Component):
    def __init__(self, robot):
        Component.__init__(self, robot)
        self._hold_repeat = False


    async def set_held_time(self, time):
        await self.rpc.held_time(time)
        self._held_time = time

    async def set_hold_repeat(self, repeat):
        await self.rpc.hold_repeat(repeat)
        self._hold_repeat = repeat

    async def set_double_press_interval(self, interval):
        self._robot._double_press_interval = interval

    @property
    def pressed(self):
        return self._robot._sensor_data['pressed']

    @property
    def when_pressed(self):
        return self._robot._sensor_callback['pressed']

    @when_pressed.setter
    def when_pressed(self, cb):
        self._robot._sensor_callback['pressed'] = cb

    @property
    def when_released(self):
        return self._robot._sensor_callback['released']

    @when_released.setter
    def when_released(self, cb):
        self._robot._sensor_callback['released'] = cb

    @property
    def held(self):
        return self._robot._sensor_data['held']

    @property
    def when_held(self):
        return self._robot._sensor_callback['held']

    @when_held.setter
    def when_held(self, cb):
        self._robot._sensor_callback['held'] = cb

    @property
    def double_pressed(self):
        return self._robot._sensor_data['double_pressed']

    @property
    def when_double_pressed(self):
        return self._robot._sensor_callback['double_pressed']

    @when_double_pressed.setter
    def when_double_pressed(self, cb):
        self._robot._sensor_callback['double_pressed'] = cb

