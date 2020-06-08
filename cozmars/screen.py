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
    async def fill(self, rgb, x=0, y=0, w=240, h=135):
        x, y = y, x
        w, h = h, w
        await self.rpc.fill(x, y, w, h, rgb_to_color565(rgb))

    @util.mode()
    async def set_pixel(self, x, y, rgb):
        await self.rpc.pixel(x, y, rgb_to_color565(rgb))

    @util.mode()
    def display(self, image, x=0, y=0):
        if isinstance(image, Image):
            image = np.array(image.convert("RGB"))
        w, h = image.shape[:2]
        image = np.rot90(image)
        x, y = y, x
        await self.rpc.display(image_to_data(image.astype('uint16')), x, y, w, h)

    @util.mode(force_sync=False)
    async def animate(self, gif, loop=1):
        # check resolution, then:
        await self.rpc.gif(gif, loop)


def resize_to_screen(image, resample=Image.BICUBIC):
    width, height = self.dimension
    image_ratio = image.width / image.height
    screen_ratio = width / height
    if screen_ratio < image_ratio:
        scaled_width = image.width * height // image.height
        scaled_height = height
    else:
        scaled_width = width
        scaled_height = image.height * width // image.width
    return image.resize((scaled_width, scaled_height), resample)

def rgb_to_color565(r, g=0, b=0):
    try:
        r, g, b = r
    except TypeError:
        pass
    return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3

def image_to_data(image):
    data = numpy.array(image.convert("RGB")).astype("uint16")
    color = (
    ((data[:, :, 0] & 0xF8) << 8)
    | ((data[:, :, 1] & 0xFC) << 3)
    | (data[:, :, 2] >> 3)
    )
    return numpy.dstack(((color >> 8) & 0xFF, color & 0xFF)).flatten().tolist()
