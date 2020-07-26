import asyncio
import numpy as np
import cv2
import random
from . import util

class EyeAnimation(util.Component):
    """屏幕上的眼睛动画"""
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self._exp_list = ['auto', 'happy', 'sad', 'surprised', 'angry', 'neutral', 'focused', 'sleepy']
        self._canvas = np.zeros((134, 240, 3), np.uint8)
        self._size = 80
        self._radius = self._size // 4
        self._eye = np.zeros((self._size, self._size, 3), np.uint8)
        self._expression = 'auto'
        self._gap = 20
        self._offset = (0, 0)
        self._color = (255, 255, 0) # cyan
        self._ev = self._exp_q = None

    @util.mode(property_type='setter')
    async def color(self, color=None):
        """眼睛的颜色，默认是青色"""
        if color:
            self._color = color
            self._create_eye()
        else:
            return self._color

    def _create_eye(self):
        color = self._color
        sr = self._size - self._radius -1
        cv2.circle(self._eye, (sr, sr), self._radius, color, -1)
        cv2.circle(self._eye, (sr, self._radius), self._radius, color, -1)
        cv2.circle(self._eye, (self._radius, sr), self._radius, color, -1)
        cv2.circle(self._eye, (self._radius, self._radius), self._radius, color, -1)
        cv2.rectangle(self._eye, (self._radius, 0), (sr, self._size-1), color, -1)
        cv2.rectangle(self._eye, (0, self._radius), (self._size-1, sr), color, -1)

    @property
    def expression_list(self):
        """支持的表情列表， `['auto', 'happy', 'sad', 'surprised', 'angry', 'neutral', 'focused', 'sleepy']` ，只读"""
        return list(self._exp_list)

    @util.mode(property_type='setter')
    async def expression(self, *args):
        """表情，默认为 `'auto'`，在所有的表情间随机切换"""
        if args:
            await self._set_exp(args[0])
        else:
            return self._expression.split('.')[0]

    @util.mode()
    async def hide(self):
        """隐藏"""
        await self._set_exp('hidden', True)

    @util.mode()
    async def stop(self):
        """暂停动态效果"""
        await self._set_exp('stopped', True)

    async def _set_exp(self, exp, wait=False):
        if self._expression != exp:
            if self._exp_q:
                self._exp_q.full() and self._exp_q.get_nowait()
                self._exp_q.put_nowait(exp)
            else:
                self._expression = exp
            wait and self._ev and (await self._ev.wait()) and self._ev.clear()

    @util.mode()
    async def show(self, exp=None):
        """显示"""
        await self._set_exp(exp or 'auto')

    # very urgly coded eye animation
    async def animate(self, robot, ignored):
        self._ev = asyncio.Event()
        self._exp_q = asyncio.Queue(1)
        self._create_eye()
        H, W = self._canvas.shape[:2]
        LX, RX, Y = (W-self._gap-self._size)//2, (W+self._size+self._gap)//2, H//2
        olpos, orpos = (LX, Y), (RX, Y)
        ox0, oy0, ox1, oy1 = LX-self._size//2, Y-self._size//2, RX+self._size//2-1, Y+self._size//2-1

        while True:

            duration = random.random() *4 + 1
            blink = False
            lresize = rresize = (self._size, self._size)
            rlbrow = llbrow = 0
            ltbrow = rtbrow = (0, 0)

            try:
                self._expression = await asyncio.wait_for(self._exp_q.get(), timeout=duration)
                if self._expression == 'hidden':
                    await robot.screen.fill((0,0,0), aio_mode=True)
                    self._ev.set()
                    while True:
                        self._expression = await self._exp_q.get()
                        if self._expression != 'hidden':
                            break
                elif self._expression == 'stopped':
                    while True:
                        if self._expression != 'stopped':
                            break
            except asyncio.TimeoutError:
                pass

            if self._expression == 'auto' or 'neutral' in self._expression:
                x, y = random.randint(-3, 3)*10, random.randint(-3, 3)*9
                lpos, rpos = (LX+x, Y+y), (RX+x, Y+y)

                # looking up -> may blink
                blink = random.random() >.2 and (oy1-oy0) >=40

                # looking aside -> different size
                resize = round(random.random(), 1)
                if resize > .65 and y < 10:
                    resize = round(self._size* resize)
                    if x > 0:
                        lresize = self._size, resize
                    elif x< 0:
                        rresize = self._size, resize

                # looking down -> eyelids half closed
                elif y > 10 or y > 0 and random.random()>.5:
                    ltbrow = rtbrow = self._size//4*(y//9), 0

                if self._expression == 'auto' and random.random() > .75:
                    self._expression = f'auto.{random.choice(self._exp_list)}'

            elif self._expression == 'auto.auto':
                await asyncio.sleep(duration/2)
                self._expression = 'auto'
                continue

            elif 'sleepy' in self._expression:
                x, y = random.randint(-1, 1)*10, random.randint(2, 3)*9
                lpos, rpos = (LX+x, Y+y), (RX+x, Y+y)
                ltbrow = rtbrow = (self._size//4*(y//9), 0)
                duration = random.random() * 3 + 2
                if 'auto.' in self._expression and random.random() >.8:
                        self._expression = 'auto'

            elif 'happy' in self._expression:
                x, y = random.randint(-3, 3)*5, random.randint(-3, -2)*9
                lpos, rpos = (LX+x, Y+y), (RX+x, Y+y)
                llbrow = rlbrow = (self._size//4)*random.randint(1,2)
                if 'auto.' in self._expression and random.random() >.6:
                    self._expression = 'auto'

            elif 'sad' in self._expression:
                blink = random.random()>.5 and (oy1-oy0) >=40
                x, y = random.randint(-3, 3)*10, random.randint(0, 2)*9
                lpos, rpos = (LX+x, Y+y), (RX+x, Y+y)
                ltbrow = rtbrow = (self._size//4*(y//9), -self._size//4)
                if 'auto.' in self._expression and random.random() >.5:
                    self._expression = 'auto'

            elif 'angry' in self._expression:
                blink = random.random()>.5 and (oy1-oy0) >=40
                x, y = random.randint(-3, 3)*10, random.randint(-2, 0)*9
                lpos, rpos = (LX+x, Y+y), (RX+x, Y+y)
                ltbrow = rtbrow = (self._size//4*(y//-9), self._size//4)
                if 'auto.' in self._expression and random.random() >.75:
                    self._expression = 'auto'

            elif 'focused' in self._expression:
                x, y = random.randint(-3, 3)*10, random.randint(-2, 2)*9
                lpos, rpos = (LX+x, Y+y), (RX+x, Y+y)
                lresize, rresize = (self._size, round(round(random.random()*.1+.4, 1)*self._size)), (self._size, round(round(random.random()*.1+.4, 1)*self._size))
                if 'auto.' in self._expression and random.random() >.65:
                    self._expression = 'auto'

            elif 'surprised' in self._expression:
                blink = random.random()>.5 and (oy1-oy0) >=40
                x, y = random.randint(-2, 2)*10, random.randint(-2, 1)*8
                lpos, rpos = (LX+x, Y+y), (RX+x, Y+y)
                enlarged = round(self._size * 1.22)
                lresize = rresize = (enlarged, enlarged)
                if 'auto.' in self._expression and random.random() >.3:
                    self._expression = 'auto'

            if blink:
                yt = oy1-(oy1-oy0)//3
                self._canvas[oy0: yt, ox0: ox1] = (0, 0, 0)
                await robot.screen.display(self._canvas[oy0: yt, ox0: ox1], ox0, oy0, aio_mode=True)
                oy0 = yt

            self._canvas[oy0: oy1, ox0: ox1] = (0, 0, 0)

            ly0, ly1, lx0, lx1 = lpos[1]-lresize[1]//2+ltbrow[0], lpos[1]+lresize[1]//2-llbrow, lpos[0]-lresize[0]//2, lpos[0]+lresize[0]//2
            e = self._eye if lresize==(self._size, self._size) else cv2.resize(self._eye, lresize)
            self._canvas[ly0: ly1, lx0: lx1] = e[ltbrow[0]: lresize[1]-llbrow]
            if ltbrow[1]:
                cv2.fillConvexPoly(self._canvas[ly0: ly1, lx0: lx1], np.array([(0,0), (lresize[0], 0), (lresize[0], ltbrow[1]) if ltbrow[1]>0 else (0, -ltbrow[1])]), (0, 0, 0))

            ry0, ry1, rx0, rx1 = rpos[1]-rresize[1]//2+rtbrow[0], rpos[1]+rresize[1]//2-rlbrow, rpos[0]-rresize[0]//2, rpos[0]+rresize[0]//2
            e = self._eye if rresize==(self._size, self._size) else cv2.resize(self._eye, rresize)
            self._canvas[ry0: ry1, rx0: rx1] = e[rtbrow[0]: rresize[1]-rlbrow]
            if ltbrow[1]:
                cv2.fillConvexPoly(self._canvas[ry0: ry1, rx0: rx1], np.array([(0,0), (rresize[0], 0), (0, rtbrow[1]) if ltbrow[1]>0 else (rresize[0], -ltbrow[1])]), (0, 0, 0))

            x0, y0, w, h = cv2.boundingRect(np.array([(lx0, ly0), (lx1, ly1), (rx0, ry0), (rx1, ry1)]))
            x1, y1 = x0+w, y0+h
            bx, by, bw, bh = cv2.boundingRect(np.array([(x0, y0), (x1-1, y1-1), (ox0, oy0), (ox1, oy1)]))
            await robot.screen.display(self._canvas[by:by+bh, bx:bx+bw], bx, by, aio_mode=True)

            ox0, oy0, ox1, oy1 = x0, y0, x1, y1
            olpos, orpos = lpos, rpos


animations = {
}
