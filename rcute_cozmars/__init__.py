"""
rcute-cozmars is the Python SDK for Cozmars, the 3D printable educational robot.

rcute-cozmars provides basic control over the robot, it can be used with `rcute-ai <https://rcute-ai.readthedocs.io>`_ for image/speech recognition and etc.

"""
from .robot import Robot, AsyncRobot, AioRobot
from .cube import Cube, AsyncCube, AioCube
from .animation import animations
from .version import __version__
