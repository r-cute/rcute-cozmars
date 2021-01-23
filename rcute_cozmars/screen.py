from . import util
from . import led
import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw

class Screen(led.LED):

    def __init__(self, robot):
        led.LED.__init__(self, robot)

    def _light_rpc(self):
        return self._rpc.backlight

    @property
    def resolution(self):
        """ `(240, 135)`, read-only """
        return 240, 135

    @util.mode()
    async def fill(self, color, x=0, y=0, w=240, h=135, stop_eyes=True):
        """Fill the screen in block

        :param color: BGR mode
        :type color: str/tuple
        :param x: The x coordinate of the upper left corner of the filled square, the default is `0`
        :type x: int
        :param y: The y coordinate of the upper left corner of the filled square, the default is `0`
        :type y: int
        :param w: the width of the filled square, the default is the screen width `240`
        :type w: int
        :param h: The width of the filled square, the default is the screen height `135`
        :type h: int
        :raises ValueError: throw an exception when the filled area exceeds the screen area
        """
        if not self._in_range((x, y), (w, h)):
            raise ValueError(f'Fill area must not exceed dimensions of screen {self.resolution}')
        x, y = y, 240-x-w
        stop_eyes and (await self._robot.eyes.stop())
        await self._rpc.fill(bgr_to_color565(util.bgr(color)), x, y, h, w)

    @util.mode()
    async def set_pixel(self, x, y, color):
        """Set color of a pixel on screen.

        :param x: the x coordinate of the pixel to be set
        :type x: int
        :param y: the y coordinate of the pixel to be set
        :type y: int
        :param color: BGR mode
        :type color: str/tuple
        :raises ValueError: An exception is thrown when the coordinates exceed the screen area
        """
        if not self._in_range((x, y)):
            raise ValueError(f'Pixel must not exceed dimensions of screen {self.resolution}')
        x, y = y, 240-x-1
        await self._rpc.pixel(x, y, bgr_to_color565(util.bgr(color)))

    @util.mode()
    async def block_display(self, image, x, y):
        """display an image on the screen starting from (x, y)

        raises AssertionError: raise error when the area to display exceeds screen
        """
        h, w = image.shape[:2]
        assert self._in_range((x, y), (x+w-1, y+h-1)), 'Display area must not exceed dimensions of screen {self.resolution}'
        x, y = y, 240-x-w
        await self._rpc.display(image_to_data(np.rot90(image)), x, y, x+h-1, y+w-1)

    @util.mode()
    async def display(self, image, stop_eyes=True):
        """Display an image

        :param image: BGR image to be displayed. The image will be resized to fit the screen,
        :type image: PIL.Image/numpy.ndarray
        """
        if isinstance(image, Image.Image):
            image = np.array(image)
        x, y, image = self._resize_to_screen(image)
        W, H = self.resolution
        filled_img = np.zeros((H, W, 3), np.uint8)
        h, w = image.shape[:2]
        filled_img[y: y+h, x: x+w] = image
        stop_eyes and (await self._robot.eyes._set_exp('stopped', True))
        await self._rpc.display(image_to_data(np.rot90(filled_img)), 0, 0, H-1, W-1)

    @util.mode()
    async def text(self, text, size=30, color='cyan', bg_color='black', font=None, stop_eyes=True):
        """Display simple text

        :param text: text to be displayed
        :type text: str
        :param size: font size, default is 30
        :type size: int, optional
        :param color: text color, default is cyan
        :type color: str/tuple, optional
        :param bg_color: background color, the default is black
        :type bg_color: str/tuple, optional
        :param font: Font file, Microsoft Yahei is used by default, it includes Chinese and English chars.
        :type font: str, optional
        """
        font = ImageFont.truetype(font or util.resource('msyh.ttc'), size)
        image = Image.new("RGB", self.resolution, util.bgr(bg_color))
        draw = ImageDraw.Draw(image)
        location = tuple((a-b)/2 for a, b in zip(self.resolution, font.getsize(text)))
        draw.text(location, text, fill=util.bgr(color), font=font)
        # W, H = self.resolution
        # image = np.zeros((H, W, 3), np.uint8)
        # image = cv2.putText(image, text, ((W-20*len(text))//2, 75), cv2.FONT_HERSHEY_SIMPLEX, 1.5, util.bgr(color), 2)
        return await self.display(np.array(image), stop_eyes=stop_eyes)

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