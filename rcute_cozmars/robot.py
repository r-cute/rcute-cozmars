"""
rcute_cozmars.robot 模块包括 :class:`Robot`, :class:`AsyncRobot` 和 :class:`AioRobot` 三个用于连接和控制 Cozmars 机器人的类：

:class:`Robot` 会以阻塞的方式顺序执行每一条指令；

:class:`AsyncRobot` 遇到耗时的指令时会以非阻塞的方式立即返回一个 :class:`concurrent.futures.Future` 后续可用于获得该指令最终的返回结果，并立即执行下一条指令；

:class:`AioRobot` 则是以异步 (async/await) 的方式执行指令

.. |pypi上的最新版本| raw:: html

   <a href='https://pypi.org/project/rcute-cozmars-server' target='blank'>pypi上的最新版本</a>

.. warning::

   Cozmars 机器人只能同时被一个程序控制，如果正在用 Scratch 控制 Cozmars，Python 程序将不能连接，反之亦然

"""

import asyncio
import aiohttp
import websockets
import threading
import logging
import json
from wsmprpc import RPCClient, RPCStream
from . import util, screen, camera, microphone, button, sonar, infrared, lift, head, buzzer, motor, eye_animation, cube_animation

logger = logging.getLogger("rcute-cozmars")

animations = {}
animations.update(cube_animation.animations)

class AioRobot:
    """Cozmars 机器人的异步 (async/await) 模式

    :param serial_or_ip: 要连接的 Cozmars 的 IP 地址或序列号
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        self._host = 'rcute-cozmars-' + serial_or_ip + '.local' if len(serial_or_ip) == 4 else serial_or_ip
        self._mode = 'aio'
        self._connected = False
        self._screen = screen.Screen(self)
        self._camera = camera.Camera(self)
        self._microphone = microphone.Microphone(self)
        self._button = button.Button(self)
        self._sonar = sonar.Sonar(self)
        self._infrared = infrared.Infrared(self)
        self._lift = lift.Lift(self)
        self._head = head.Head(self)
        self._buzzer = buzzer.Buzzer(self)
        self._motor = motor.Motor(self)
        self._eye_anim = eye_animation.EyeAnimation(self)

    def _in_event_loop(self):
        return True

    @util.mode()
    async def animate(self, name, *args, **kwargs):
        """执行动作

        :param name: 动作的名称
        :type name: str
        """
        anim = animations[name]
        anim = getattr(anim, 'animate', anim)
        await anim(self, *args, **kwargs)

    @property
    def animation_list(self):
        """动作列表"""
        return list(animations.keys())

    @util.mode()
    async def pick_up_cube(self, height=1, debug=False):
        """拾取魔方

        :param debug: 默认为 `False`，设为 `True` 则会显示摄像头画面
        :type debug: bool
        """
        return await animations['pick_up_cube'](self, height, debug=debug)

    @util.mode()
    async def put_down_cube(self, height=0):
        """放下魔方"""
        return await animations['put_down_cube'](self, height)

    @property
    def eyes(self):
        """眼睛"""
        return self._eye_anim

    @property
    def button(self):
        """按钮"""
        return self._button

    @property
    def infrared(self):
        """红外传感器，在机器人底部"""
        return self._infrared

    @property
    def sonar(self):
        """声纳，即超声波距离传感器"""
        return self._sonar

    @property
    def motor(self):
        """马达"""
        return self._motor

    @property
    def head(self):
        """头"""
        return self._head

    @property
    def lift(self):
        """手臂"""
        return self._lift

    @property
    def buzzer(self):
        """蜂鸣器"""
        return self._buzzer

    @property
    def screen(self):
        """屏幕"""
        return self._screen

    @property
    def camera(self):
        """摄像头"""
        return self._camera

    @property
    def microphone(self):
        """麦克风"""
        return self._microphone

    async def connect(self):
        """连接 Cozmars"""
        if not self._connected:
            self._ws = await websockets.connect(f'ws://{self._host}/rpc')
            if '-1' == await self._ws.recv():
                raise RuntimeError('无法连接 Cozmars, 请先关闭其他已经连接 Cozmars 的程序')
            self._rpc = RPCClient(self._ws)
            about = json.loads(await self._get('/about'))
            self._ip = about['ip']
            self._serial = about['serial']
            self._firmware_version = about['version']
            self._hostname = about['hostname']
            self._mac = about['mac']
            self._sensor_task = asyncio.create_task(self._get_sensor_data())
            self._eye_anim_task = asyncio.create_task(self._eye_anim.animate(self))
            self._connected = True

    @property
    def connected(self):
        """是否连接上了机器人"""
        return self._connected

    async def _call_callback(self, cb, *args):
        if cb:
            if self._mode == 'aio':
                (await cb(*args)) if asyncio.iscoroutinefunction(cb) else cb(*args)
            else:
                self._lo.run_in_executor(None, cb, *args)

    async def _get_sensor_data(self):
        self._sensor_data_rpc = self._rpc.sensor_data()
        async for event, data in self._sensor_data_rpc:
            try:
                if event == 'pressed':
                    if not data:
                        self.button._held = self.button._double_pressed = False
                    self.button._pressed = data
                    await self._call_callback(self.button.when_pressed if data else self.button.when_released)
                elif event == 'held':
                    self.button._held = data
                    await self._call_callback(self.button.when_held)
                elif event == 'double_pressed':
                    self.button._pressed = data
                    self.button._double_pressed = data
                    await self._call_callback(self.button.when_pressed)
                    await self._call_callback(self.button.when_double_pressed)
                elif event == 'out_of_range':
                    await self._call_callback(self.sonar.when_out_of_range, data)
                elif event == 'in_range':
                    await self._call_callback(self.sonar.when_in_range, data)
                elif event == 'lir':
                    self.infrared._state = data, self.infrared._state[1]
                    await self._call_callback(self.infrared.when_state_changed, self.infrared._state)
                elif event == 'rir':
                    self.infrared._state = self.infrared._state[0], data
                    await self._call_callback(self.infrared.when_state_changed, self.infrared._state)
            except Exception as e:
                logger.exception(e)

    async def disconnect(self):
        """断开 Cozmars 的连接"""
        if self._connected:
            self._sensor_task.cancel()
            self._eye_anim_task.cancel()
            self._sensor_data_rpc.cancel()
            await asyncio.gather(self.camera._close(), self.microphone._close(), self.buzzer._close(), return_exceptions=True)
            await self._ws.close()
            self._connected = False

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    @util.mode(force_sync=False)
    async def forward(self, duration=None):
        """前进

        :param duration: 持续时间（秒）
        :type duration: float
        """
        await self._rpc.speed((1,1), duration)

    @util.mode(force_sync=False)
    async def backward(self, duration=None):
        """后退

        :param duration: 持续时间（秒）
        :type duration: float
        """
        await self._rpc.speed((-1,-1), duration)

    @util.mode(force_sync=False)
    async def turn_left(self, duration=None):
        """左传

        :param duration: 持续时间（秒）
        :type duration: float
        """
        await self._rpc.speed((-1,1), duration)

    @util.mode(force_sync=False)
    async def turn_right(self, duration=None):
        """右转

        :param duration: 持续时间（秒）
        :type duration: float
        """
        await self._rpc.speed((1,-1), duration)

    @util.mode()
    async def stop(self):
        """停止"""
        await self._rpc.speed((0, 0))

    @property
    def hostname(self):
        """Cozmars 的网址"""
        return self._hostname

    @property
    def ip(self):
        """Cozmars 的 IP 地址"""
        return self._ip

    @property
    def firmware_version(self):
        """Cozmars 的固件版本

        如果低于 |pypi上的最新版本| ，可以登陆机器人的页面进行更新

        """
        return self._firmware_version

    @property
    def mac(self):
        """Cozmars 的 MAC 地址"""
        return self._mac


    @property
    def serial(self):
        """Cozmars 的序列号"""
        return self._serial

    @util.mode()
    async def poweroff(self):
        """关闭 Cozmars"""
        await AioRobot.disconnect(self)
        try:
            await self._get('/poweroff')
        except Exception as e:
            pass

    @util.mode()
    async def reboot(self):
        """重启 Cozmars"""
        await AioRobot.disconnect(self)
        try:
            await self._get('/reboot')
        except Exception as e:
            pass

    async def _get(self, sub_url):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://' + self._host + sub_url) as resp:
                return await resp.text()

class Robot(AioRobot):
    """Cozmars 机器人的同步模式

    :param serial_or_ip: 要连接的 Cozmars 的 IP 地址或序列号
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        AioRobot.__init__(self, serial_or_ip)
        self._mode = 'sync'

    def _in_event_loop(self):
        return self._event_thread == threading.current_thread()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.disconnect()

    def connect(self):
        """连接 Cozmars"""
        self._lo = asyncio.new_event_loop()
        self._event_thread = threading.Thread(target=self._run_loop, args=(self._lo,), daemon=True)
        self._event_thread.start()
        asyncio.run_coroutine_threadsafe(AioRobot.connect(self), self._lo).result()

    def disconnect(self):
        """断开 Cozmars 的连接"""
        asyncio.run_coroutine_threadsafe(AioRobot.disconnect(self), self._lo).result()
        self._lo.call_soon_threadsafe(self._done_ev.set)
        self._event_thread.join(timeout=5)

    def _run_loop(self, loop):
        asyncio.set_event_loop(loop)
        self._done_ev = asyncio.Event()
        loop.run_until_complete(self._done_ev.wait())
        tasks = asyncio.all_tasks(loop)
        for t in tasks:
            t.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)

class AsyncRobot(Robot):
    """Cozmars 机器人的异步 (concurrent.futures.Future) 模式

    :param serial_or_ip: 要连接的 Cozmars 的 IP 地址或序列号
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        Robot.__init__(self, serial_or_ip)
        self._mode = 'async'


