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

    @util.mode(property_type='setter')
    async def held_time(self, *args):
        return await self.rpc.held_time(*args)

    @util.mode(property_type='setter')
    async def hold_repeat(self, *args):
        return await self.rpc.hold_repeat(*args)

    @util.mode(property_type='setter')
    async def double_press_max_interval(self, *args):
        return await self.rpc.double_press_max_interval(*args)
