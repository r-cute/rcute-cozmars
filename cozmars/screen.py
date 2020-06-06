from . import error, util
from PIL import Image

class Screen(util.Component):
    def __init__(self, robot):
        util.Component.__init__(self, robot)
        self.default_fade_speed = None

    @property
    def resolution(self):
        return (240, 135)

    @util.mode()
    async def fill(self, rgb):
        await self.rpc.fill(rgb)

    @util.mode()
    async def set_pixel(self, pos, rgb):
        await self.rpc.pixel(pos, rgb)

    @util.mode(property_type='setter')
    async def brightness(self, *args):
        return await self.rpc.backlight(*args)

    @util.mode(force_sync=False)
    async def set_brightness(self, brightness, *, duration=None, fade_speed=None):
        await self.rpc.backlight(brightness, duration, fade_speed or self.default_fade_speed)

    @util.mode()
    async def display(self, image, resample):
        # check_dimention
        await self.rpc.image(image)

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
