"""
rcute-cozmars 是3d打印教育机器人 Cozmars 的 Python SDK，实现对机器人的基本控制，并可以结合 |rcute-ai| 完成图像/语音识别等功能

.. |rcute-ai| raw:: html

   <a href='https://rcute-ai.readthedocs.io' target='blank'>rcute-ai</a>

"""

from .robot import Robot, AsyncRobot, AioRobot
from .cube import Cube, AsyncCube, AioCube
from .version import __version__
