from .util import mode, Component
from . import error
from PIL import Image

class Screen(Component):

    @property
    def dimension(self):
        return (240, 135)

    @mode()
    async def fill(self, rgb):
        await self.rpc.fill(rgb)

    @mode()
    async def set_pixel(self, pos, rgb):
        await self.rpc.pixel(pos, rgb)

    @mode()
    async def set_backlight(self, level):
        await self.rpc.backlight(level)

    @mode()
    async def display(self, image, resample):
        image = self.resize(image, resample)
        await self.rpc.image(image)

    def resize(image, resample=Image.BICUBIC):
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



