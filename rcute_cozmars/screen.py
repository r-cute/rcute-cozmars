from. import util
import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw

class Screen(util.Component):
    """Display"""

    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.default_fade_speed = None
        """The default gradient speed when setting :data:`brightness`, the default is `None`, which means there is no gradient"""

    @property
    def resolution(self):
        """Resolution, `(240, 135)`, read-only """
        return 240, 135

    @property
    def max_brightness(self):
        """Maximum brightness, `1.0`, read-only"""
        return 1.0

    @property
    def min_brightness(self):
        """Minimum brightness, ie black screen, `0.0`, read only"""
        return .0

    @util.mode(property_type='setter')
    async def brightness(self, *args):
        """Display brightness, 0~1, default is `0.05`
        """
        if args:
            await self._rpc.backlight(args[0], None, self.default_fade_speed)
        else:
            return round(await self._rpc.backlight(), 2)

    @util.mode(force_sync=False)
    async def set_brightness(self, brightness, *, fade_duration=None, fade_speed=None):
        """Set display brightness

        :param brightness: brightness, 0~1
        :type brightness: float
        :param fade_duration: fade time (seconds), the default is `None`, which means no fade
        :type fade_duration: float
        :param fade_speed: fade speed (/sec), the default is `None`, which means no fade
        :type fade_speed: float
        :raises TypeError: `fade_duration` and `fade_speed` cannot be set at the same time, otherwise an exception will be thrown
        """
        if fade_duration and fade_speed:
            raise TypeError('Cannot set both fade_duration and fade_speed')
        await self._rpc.backlight(brightness, fade_duration, fade_speed)

    @util.mode()
    async def fill(self, color, x=0, y=0, w=240, h=135, stop_eyes=True):
        """Fill the screen

        :param color: the color to be filled (bgr mode)
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
        """Set the color of the pixel

        :param x: the x coordinate of the pixel to be set
        :type x: int
        :param y: the y coordinate of the pixel to be set
        :type y: int
        :param color: color (bgr mode)
        :type color: str/tuple
        :raises ValueError: An exception is thrown when the coordinates exceed the screen range
        """
        if not self._in_range((x, y)):
            raise ValueError(f'Pixel must not exceed dimensions of screen {self.resolution}')
        x, y = y, 240-x-1
        await self._rpc.pixel(x, y, bgr_to_color565(util.bgr(color)))

    @util.mode()
    async def block_display(self, image, x, y):
        """display the image on a on the screen from (x, y)

        raises AssertionError: raise error when the area to display exceeds screen
        """
        h, w = image.shape[:2]
        assert self._in_range((x, y), (x+w-1, y+h-1)),'Display area must not exceed dimensions of screen {self.resolution}'
        x, y = y, 240-x-w
        await self._rpc.display(image_to_data(np.rot90(image)), x, y, x+h-1, y+w-1)

    @util.mode()
    async def display(self, image, stop_eyes=True):
        """Display image

        :param image: the image to be displayed (bgr mode)
        :type image: numpy.ndarray
        """
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

        :param text: the text to be displayed
        :type text: str
        :param size: font size, default is 30
        :type size: int, optional
        :param color: text color, default is cyan
        :type color: str/tuple, optional
        :param bg_color: background color, the default is black
        :type bg_color: str/tuple, optional
        :param font: Font file, Microsoft Yahei is used by default (Chinese/English is supported)
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
        if W/H> w/h:
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