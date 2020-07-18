import asyncio
import numpy as np
import cv2
import random
from . import util

class EyeAnimation(util.Component):
    """屏幕上的眼睛动画"""
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self._exp_list = ['auto', 'happy', 'sad', 'surprised', 'angry', 'neutral']
        self._canvas = np.zeros((134, 240, 3), np.uint8)
        self._size = 80
        self._radius = self._size // 4
        self._eye = np.zeros((self._size, self._size, 3), np.uint8)
        self._expression = 'hidden'
        self._gap = 20
        self._offset = (0, 0)
        self._color = (255, 255, 0) # cyan

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
        """支持的表情列表， `['auto', 'happy', 'sad', 'surprised', 'angry', 'neutral']` ，只读"""
        return list(self._exp_list)

    @util.mode(property_type='setter')
    async def expression(self, *args):
        """表情，默认为 `'auto'` """
        if args:
            ex = args[0].split('.')
            assert ex[0] in self._exp_list and ex[-1] in self._exp_list, f'Expression must be one of {self.expression_list}'
            self._exp_q.full() and self._exp_q.get_nowait()
            self._exp_q.put_nowait(args[0])
        else:
            return self._expression.split('.')[0]

    @util.mode()
    async def hide(self):
        """隐藏"""
        self._exp_q.full() and self._exp_q.get_nowait()
        self._exp_q.put_nowait('hidden')

    @util.mode()
    async def show(self, exp=None):
        """显示"""
        self._exp_q.full() and self._exp_q.get_nowait()
        self._exp_q.put_nowait(exp or 'auto')

    # very urgly coded eye animation
    async def animate(self, robot, ignored):
        async def blink():
            nonlocal oy1, oy0, ox0, ox1
            yt = oy1-(oy1-oy0)//3
            self._canvas[oy0: yt, ox0: ox1] = (0, 0, 0)
            await robot.screen.display(self._canvas[oy0: yt, ox0: ox1], ox0, oy0, aio_mode=True)
            oy0 = yt
        self._create_eye()
        self._expression = 'auto'
        self._exp_q = asyncio.Queue(1)
        h, w = self._canvas.shape[:2]
        ox, oy = 0, 0
        ox0, oy0, ox1, oy1 = w//2 - self._gap//2 - self._size, (h-self._size)//2, w//2 + self._size + self._gap//2, (h+self._size)//2
        X0, Y0, X1, Y1 = ox0, oy0, ox1, oy1
        while True:
            if self._expression == 'auto' or 'neutral' in self._expression:
                x, y = random.randint(-3, 3)*10, random.randint(-3, 3)*9

                # looking up -> may blink
                if oy >= y and random.random() >.2:
                    await blink()

                self._canvas[oy0: oy1, ox0: ox1] = (0, 0, 0)
                x0, y0, x1, y1 = X0+ x, Y0+ y, X1+ x, Y1+ y

                resize = round(random.random(), 1)
                if resize > .65 and y < 10:
                    resized_eye = cv2.resize(self._eye, (self._size, round(self._size*resize)))
                    if x > 0:
                        self._canvas[round(y0+self._size*(.5-resize/2)): round(y0+self._size*(resize/2+.5)), x0: x0+self._size] = resized_eye
                        self._canvas[y1-self._size: y1, x1-self._size: x1] = self._eye
                    elif x< 0:
                        self._canvas[y0: y0+self._size, x0: x0+self._size] = self._eye
                        self._canvas[round(y1-self._size*(.5+resize/2)): round(y1+self._size*(resize/2-.5)), x1-self._size: x1] = resized_eye
                    else:
                        self._canvas[y0: y0+self._size, x0: x0+self._size] = self._eye
                        self._canvas[y1-self._size: y1, x1-self._size: x1] = self._eye

                # looking down -> eyelids half closed
                elif y > 10 or y > 0 and random.random()>.5:
                    yt = self._size//4*(y//9)
                    self._canvas[y0+yt: y0+self._size, x0: x0+self._size] = self._eye[yt:]
                    self._canvas[y1-self._size+yt: y1, x1-self._size: x1] = self._eye[yt:]
                    y0 = yt + y0

                else:
                    self._canvas[y0: y0+self._size, x0: x0+self._size] = self._eye
                    self._canvas[y1-self._size: y1, x1-self._size: x1] = self._eye

                if random.random() > .75:
                    self._expression = f'auto.{random.choice(self._exp_list)}'

            elif self._expression == 'auto.auto':
                self._expression = 'auto'

            elif 'happy' in self._expression:
                self._canvas[oy0: oy1, ox0: ox1] = (0, 0, 0)
                x, y = random.randint(-3, 3)*5, random.randint(-3, -2)*9
                yt = (self._size//4)*random.randint(1,2)
                x0, y0, x1 = X0+ x, Y0+ y, X1+ x
                y1 = y0 + yt
                self._canvas[y0: y1, x0: x0+self._size] = self._eye[:yt]
                self._canvas[y0: y1, x1-self._size: x1] = self._eye[:yt]
                if 'auto.' in self._expression and random.random() >.6:
                    self._expression = 'auto'

            elif 'sad' in self._expression:
                if random.random()>.5 and oy <= 9:
                    await blink()
                self._canvas[oy0: oy1, ox0: ox1] = (0, 0, 0)
                x, y = random.randint(-3, 3)*10, random.randint(0, 2)*9
                x0, y0, x1, y1 = X0+ x, Y0+ y, X1+ x, Y1+ y
                yt = self._size//4*(y//9)
                self._canvas[y0+yt: y0+self._size, x0: x0+self._size] = self._eye[yt:]
                self._canvas[y1-self._size+yt: y1, x1-self._size: x1] = self._eye[yt:]
                cv2.fillConvexPoly(self._canvas[y0+yt: y0+self._size, x0: x0+self._size], np.array([(0,0), (self._size,0), (0,self._size//4)]), (0,0,0))
                cv2.fillConvexPoly(self._canvas[y1-self._size+yt: y1, x1-self._size: x1], np.array([(0,0), (self._size,0), (self._size,self._size//4)]), (0,0,0))
                y0 = y0 + yt
                if 'auto.' in self._expression and random.random() >.5:
                    self._expression = 'auto'

            elif 'angry' in self._expression:
                if random.random()>.5 and oy <= -9:
                    await blink()
                self._canvas[oy0: oy1, ox0: ox1] = (0, 0, 0)
                x, y = random.randint(-3, 3)*10, random.randint(-2, 0)*9
                x0, y0, x1, y1 = X0+ x, Y0+ y, X1+ x, Y1+ y
                yt = self._size//4*(y//-9)
                self._canvas[y0+yt: y0+self._size, x0: x0+self._size] = self._eye[yt:]
                self._canvas[y1-self._size+yt: y1, x1-self._size: x1] = self._eye[yt:]
                cv2.fillConvexPoly(self._canvas[y0+yt: y0+self._size, x0: x0+self._size], np.array([(0,0), (self._size,0), (self._size,self._size//4)]), (0,0,0))
                cv2.fillConvexPoly(self._canvas[y1-self._size+yt: y1, x1-self._size: x1], np.array([(0,0), (self._size,0), (0,self._size//4)]), (0,0,0))
                y0 = y0 + yt
                if 'auto.' in self._expression and random.random() >.75:
                    self._expression = 'auto'

            elif 'surprised' in self._expression:
                if random.random()> .5:
                    await blink()
                self._canvas[oy0: oy1, ox0: ox1] = (0, 0, 0)
                x, y = random.randint(-2, 2)*10, random.randint(-2, 1)*8
                enlarged = round(self._size*.22)
                large_eye = cv2.resize(self._eye, (enlarged+self._size, enlarged+self._size))
                x0, y0, x1, y1 = X0-enlarged//2+ x, Y0-enlarged//2+ y, X1+enlarged//2+ x, Y1+enlarged//2+ y
                self._canvas[y0: y1, x0: x0+self._size+enlarged] = large_eye
                self._canvas[y0: y1, x1-self._size-enlarged: x1] = large_eye
                if 'auto.' in self._expression and random.random() >.3:
                    self._expression = 'auto'

            bx, by, bw, bh = cv2.boundingRect(np.array([(x0, y0), (x1, y1), (ox0, oy0), (ox1, oy1)]))
            await robot.screen.display(self._canvas[by:by+bh, bx:bx+bw], bx, by, aio_mode=True)

            ox0, oy0, ox1, oy1 = x0, y0, x1, y1
            ox, oy = x, y

            try:
                self._expression = await asyncio.wait_for(self._exp_q.get(), timeout=random.random()*5)
                if self._expression == 'hidden':
                    await robot.screen.fill((0,0,0), aio_mode=True)
                    while True:
                        self._expression = await self._exp_q.get()
                        if self._expression != 'hidden':
                            break
            except asyncio.TimeoutError:
                pass


animations = {
}


