from . import util
import numpy as np
import cv2

class Screen(util.Component):
    """显示屏"""

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.default_fade_speed = None
        """设置 :data:`brightness` 时的默认的渐变速度，默认为 `None` ，表示没有渐变"""

    @property
    def resolution(self):
        """分辨率，`(240, 135)`，只读"""
        return 240, 135

    @property
    def max_brightness(self):
        """最大亮度， `1.0` ，只读"""
        return 1.0

    @property
    def min_brightness(self):
        """最低亮度，即黑屏， `0.0` ，只读"""
        return .0

    @util.mode(property_type='setter')
    async def brightness(self, *args):
        """显示屏亮度，0~1，默认是 `0.05`
        """
        if args:
            await self._rpc.backlight(args[0], None, self.default_fade_speed)
        else:
            return round(await self._rpc.backlight(), 2)

    @util.mode(force_sync=False)
    async def set_brightness(self, brightness, *, fade_duration=None, fade_speed=None):
        """设置显示屏亮度

        :param brightness: 亮度，0~1
        :type brightness: float
        :param fade_duration: 渐变时间（秒） ， 默认是 `None`，表示没有渐变
        :type fade_duration: float
        :param fade_speed: 渐变速度（/秒） ， 默认是 `None`，表示没有渐变
        :type fade_speed: float
        :raises TypeError: 不能同时设置 `fade_duration` 和 `fade_speed` ，否则抛出异常
        """
        if fade_duration and fade_speed:
            raise TypeError('Cannot set both fade_duration and fade_speed')
        await self._rpc.backlight(brightness, fade_duration, fade_speed)

    @util.mode()
    async def fill(self, color, x=0, y=0, w=240, h=135, stop_eyes=True):
        """填充屏幕

        :param color: 要填充的颜色（bgr 模式）
        :type color: str/tuple
        :param x: 填充方块的左上角 x 坐标，默认为 `0`
        :type x: int
        :param y: 填充方块的左上角 y 坐标，默认为 `0`
        :type y: int
        :param w: 填充方块的宽，默认为屏幕宽度 `240`
        :type w: int
        :param h: 填充方块的宽，默认为屏幕高度 `135`
        :type h: int
        :raises ValueError: 填充区域超出屏幕范围时抛出异常
        """
        if not self._in_range((x, y), (w, h)):
            raise ValueError(f'Fill area must not exceed dimensions of screen {self.resolution}')
        x, y = y, 240-x-w
        stop_eyes and (await self._robot.eyes.stop())
        await self._rpc.fill(bgr_to_color565(util.bgr(color)), x, y, h, w)

    @util.mode()
    async def set_pixel(self, x, y, color):
        """设置像素点的颜色

        :param x: 要设置的像素点的 x 坐标
        :type x: int
        :param y: 要设置的像素点的 y 坐标
        :type y: int
        :param color: 颜色（bgr 模式）
        :type color: str/tuple
        :raises ValueError: 坐标超出屏幕范围时抛出异常
        """
        if not self._in_range((x, y)):
            raise ValueError(f'Pixel must not exceed dimensions of screen {self.resolution}')
        x, y = y, 240-x-1
        await self._rpc.pixel(x, y, bgr_to_color565(util.bgr(color)))

    @util.mode()
    async def block_display(self, image, x, y):
        """display the image on a block area on the screen

        raises AssertionError: raise error when the area to display exceeds screen
        """
        h, w = image.shape[:2]
        assert self._in_range((x, y), (x+w-1, y+h-1)), 'Display area must not exceed dimensions of screen {self.resolution}'
        x, y = y, 240-x-w
        await self._rpc.display(image_to_data(np.rot90(image)), x, y, x+h-1, y+w-1)

    @util.mode()
    async def display(self, image, stop_eyes=True):
        """显示图像

        :param image: 要显示的图像（bgr 模式）
        :type image: numpy.ndarray
        """
        x, y, image = self._resize_to_screen(image)
        W, H = self.resolution
        filled_img = np.zeros((H, W, 3), np.uint8)
        h, w = image.shape[:2]
        filled_img[y: y+h, x: x+w] = image
        stop_eyes and (await self._robot.eyes._set_exp('stopped', True))
        await self._rpc.display(image_to_data(np.rot90(filled_img)), 0, 0, H-1, W-1)

    def _resize_to_screen(self, img):
        h, w = img.shape[:2]
        W, H = self.resolution
        if W/H > w/h:
            f = int(w/h*H)
            return (W-f)//2, 0, cv2.resize(img, (f, H))
        else:
            f = int(h/w*W)
            return 0, (H-f)//2, cv2.resize(img, (W, f))

    def _in_range(self, *points):
        w, h = self.resolution
        for p in points:
            if 0>p[0]>w or 0>p[1]>h:
                return False
        return True


def bgr_to_color565(b, g=0, r=0):
    try:
        b, g, r = b
    except TypeError:
        pass
    return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3

def image_to_data(bgr_image):
    bgr_image = bgr_image.astype('uint16')
    # data = numpy.array(image.convert("RGB")).astype("uint16")
    color = (
    ((bgr_image[:, :, 2] & 0xF8) << 8)
    | ((bgr_image[:, :, 1] & 0xFC) << 3)
    | (bgr_image[:, :, 0] >> 3)
    )
    return np.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()