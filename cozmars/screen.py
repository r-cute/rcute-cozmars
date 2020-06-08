from . import error, util
from PIL import Image
import numpy as np

class Screen(util.Component):
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.default_fade_speed = None

    @property
    def resolution(self):
        return 240, 135

    @util.mode(property_type='setter')
    async def brightness(self, *args):
        return await self.rpc.backlight(*args)

    @util.mode(force_sync=False)
    async def set_brightness(self, brightness, *, duration=None, fade_speed=None):
        await self.rpc.backlight(brightness, duration, fade_speed or self.default_fade_speed)

    @util.mode()
    async def fill(self, bgr, x=0, y=0, w=240, h=135):
        if not self._in_range((x, y), (w, h)):
            raise error.CozmarsError(f'Fill area must not exceed dimensions of screen {self.resolution}')
        x, y = y, 240-x-w
        await self.rpc.fill(bgr_to_color565(bgr), x, y, h, w)

    @util.mode()
    async def set_pixel(self, x, y, bgr):
        if not self._in_range((x, y)):
            raise error.CozmarsError(f'Pixel must not exceed dimensions of screen {self.resolution}')
        x, y = y, 240-x-1
        await self.rpc.pixel(x, y, bgr_to_color565(bgr))

    @util.mode()
    async def display(self, image, x=0, y=0):
        # if isinstance(image, Image):
        #     image = np.array(image.convert("RGB"))
        h, w, ch = image.shape
        if not self._in_range((x, y), (x+w, y+h)):
            raise error.CozmarsError(f'Image must not exceed dimensions of screen {self.resolution}')
        image = np.rot90(image)
        x, y = y, 240-x-w
        await self.rpc.display(image_to_data(image.astype('uint16')), x, y, x+h-1, y+w-1)

    @util.mode(force_sync=False)
    async def animate(self, gif, loop='auto'):
        await self.rpc.gif(gif, loop)

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
    # data = numpy.array(image.convert("RGB")).astype("uint16")
    color = (
    ((bgr_image[:, :, 2] & 0xF8) << 8)
    | ((bgr_image[:, :, 1] & 0xFC) << 3)
    | (bgr_image[:, :, 0] >> 3)
    )
    return np.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()
