"""
rcute-cozmars is the Python SDK of 3D printing educational robot Cozmars, which realizes basic control of the robot, and can be combined with |rcute-ai| to complete functions such as image/speech recognition

.. |rcute-ai| raw:: html

   <a href='https://rcute-ai.readthedocs.io' target='blank'>rcute-ai</a>

"""

from .robot import Robot, AsyncRobot, AioRobot
from .cube import Cube, AsyncCube, AioCube
from .animation import animations
from .version import __version__
