from . import error, util

class Button(util.Component):
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.when_held = None
        self.when_released = None
        self.when_pressed = None
        self.when_double_pressed = None
        self._pressed = False
        self._double_pressed = False
        self._held = False

    @property
    def pressed(self):
        return self._pressed

    @property
    def held(self):
        return self._held

    @property
    def double_pressed(self):
        return self._double_pressed

    @property
    def double_press_interval(self):
        return self._double_press_interval

    @property
    def held_time(self):
        return self._held_time

    @property
    def hold_repeat(self):
        return self._hold_repeat

    @util.get_set
    @util.mode()
    async def held_time(self, *args):
        return await self.rpc.held_time(*args)

    @util.get_set
    @util.mode()
    async def hold_repeat(self, *args):
        return await self.rpc.hold_repeat(*args)

    @util.get_set
    @util.mode()
    async def double_press_max_interval(self, *args):
        return await self.rpc.double_press_max_interval(*args)
