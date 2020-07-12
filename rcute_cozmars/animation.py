from . import util

class EyeAnimation:
    def __init__(self, color):
        self._eyes = {}
        self.color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    async def animate(self, robot, ignored):
        await robot.screen.fill((0,0,0))
        while True:
            await asyncio.sleep(random.randint(0, 5))



animations = {
}


