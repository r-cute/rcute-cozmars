import asyncio
from . import util

class EyeAnimation:
    """屏幕上的眼睛动画"""
    def __init__(self):
        self._exp_q = asyncio.Queue(1)
        self.color = (255, 255, 0) # cyan

    @property
    def color(self):
        """眼睛的颜色，默认是青色"""
        return self._color

    @color.setter
    def color(self, color):
        self._color = color

    @property
    def expression_list(self):
        """支持的表情列表， `['auto', 'happy', 'sad', 'surprised', 'angry', 'neutral']` ，只读"""
        return ['auto', 'happy', 'sad', 'surprised', 'angry', 'neutral']

    @util.mode(property_type='setter')
    async def expression(self, *args):
        """表情，默认为 `'auto'` """
        if args:
            assert args[0] in self.expression_list, f'Expression must be one of {self.expression_list}'
            self._exp_q.full() and self._exp_q.get_nowait()
            self._exp_q.put_nowait(args[0])
        else:
            return self._expression

    @util.mode()
    async def hide(self):
        """隐藏"""
        self._exp_q.full() and self._exp_q.get_nowait()
            self._exp_q.put_nowait('hide')

    @util.mode()
    async def show(self):
        """显示"""
        self._exp_q.full() and self._exp_q.get_nowait()
            self._exp_q.put_nowait('show')


    async def animate(self, robot, ignored):
        self._expression = 'auto'
        while True:
            try:
                next_exp = await asyncio.wait_for(self._exp_q.get(), timeout=random.randint(1, 5))
                if next_exp == 'hide':
                    while 'show' != await self._exp_q.get():
                        pass
                    continue
                elif next_exp == 'show':
                    continue
                else:
                    self._expression = next_exp
            except asyncio.TimeoutError:
                pass
            # self._expression...
            # await robot._stub.clear_and_display(...)



animations = {
}


