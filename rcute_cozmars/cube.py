import asyncio
import aiohttp
import websockets
import threading
import logging
import json
from wsmprpc import RPCClient, RPCStream
from . import util

logger = logging.getLogger("rcute-cube")

class AioCube:
    """魔方的异步 (async/await) 模式

    :param serial_or_ip: 要连接的 魔方的 IP 地址或序列号
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        self._host = 'rcute-cube-' + serial_or_ip + '.local' if len(serial_or_ip) == 4 else serial_or_ip
        self._mode = 'aio'
        self._state = 'moved'
        self._connected = False
        self._dir2color = {'+X':'red', '-X':'green', '+Y':'blue', '-Y':'yellow', '+Z':'white', '-Z':'orange'}
        self.last_action = None
        """魔方的上一个动作"""
        self.when_flipped = None
        """回调函数，当魔方被翻转时调用（带一个方向参数表示90度翻转或180度），默认为 `None` """
        self.when_shaked = None
        """回调函数，当魔方被甩动时调用，默认为 `None` """
        self.when_rotated = None
        """回调函数，当魔方被水平旋转时调用（带一个方向参数表示顺时针或逆时针），默认为 `None` """
        self.when_pushed = None
        """回调函数，当魔方被平移时调用（带一个方向参数表示移动方向），默认为 `None` """
        self.when_tilted = None
        """回调函数，当魔方被倾斜时调用（带一个方向参数表示移动方向），默认为 `None` """
        self.when_tapped = None
        """回调函数，轻敲魔方时被调用，默认为 `None` """
        self.when_fall = None
        """回调函数，当魔方失重/自由落体时调用，默认为 `None` """
        self.when_moved = None
        """回调函数，当魔方被移动时调用（包括以上动作），默认为 `None` """
        self.when_static = None
        """回调函数，当魔方恢复静止时调用，默认为 `None` """


    def _in_event_loop(self):
        return True

    async def connect(self):
        """建立与魔方的连接"""
        if not self._connected:
            self._ws = await websockets.connect(f'ws://{self._host}:81')
            if '-1' == await self._ws.recv():
                raise RuntimeError('无法连接魔方, 请先关闭其他正在连接魔方的程序')
            self._rpc = RPCClient(self._ws)
            about = json.loads(await self._get('/about'))
            self._ip = about['ip']
            self._serial = about['serial']
            self._firmware_version = about['version']
            self._hostname = about['hostname']
            self._mac = about['mac']
            self._event_task = asyncio.create_task(self._get_event())
            self._connected = True

    async def _call_callback(self, cb, *args):
        if cb:
            if self._mode == 'aio':
                (await cb(*args)) if asyncio.iscoroutinefunction(cb) else cb(*args)
            else:
                self._lo.run_in_executor(None, cb, *args)

    async def _get_event(self):
        self._event_rpc = self._rpc.mpu_event()
        async for event in self._event_rpc:
            try:
                arg = self._dir2color.get(event[1], event[1])
                if event[0] in ('static', 'moved'):
                    self._state = event[0]
                else:
                    self.last_action = event[0], arg
                if event[0] in ('static', 'moved', 'fall', 'tapped', 'shaked'):
                    await self._call_callback(getattr(self, 'when_'+event[0]))
                else:
                    await self._call_callback(getattr(self, 'when_'+event[0]), arg)
            except Exception as e:
                logger.exception(e)

    @property
    def connected(self):
        """是否连接上了魔方"""
        return self._connected

    async def disconnect(self):
        """断开与魔方的连接"""
        if self._connected:
            self._event_rpc.cancel()
            await asyncio.gather(self._event_task, return_exceptions=True)
            await self._ws.close()
            self._connected = False

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    @property
    def ip(self):
        """魔方的 IP 地址"""
        return self._ip

    @property
    def hostname(self):
        """魔方的网址"""
        return self._hostname

    @property
    def firmware_version(self):
        """魔方的固件版本"""
        return self._firmware_version

    @property
    def mac(self):
        """魔方的 MAC 地址"""
        return self._mac

    @property
    def serial(self):
        """魔方的序列号"""
        return self._serial

    async def _get(self, sub_url):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://' + self._host + sub_url) as resp:
                return await resp.text()

    @util.mode(property_type='setter')
    async def color(self, *args):
        """LED 灯的 BGR 颜色"""
        if args:
            await self._rpc.rgb(*(util.bgr(args[0]) if args[0] is not None else (0,0,0))[::-1])
        else:
            return (await self._rpc.rgb())[::-1]

    @util.mode(property_type='getter')
    async def acc(self):
        """加速度失量，当魔方静止时，加速度等于重力加速度（但实际上是有误差的）"""
        return await self._rpc.mpu_acc()

    @util.mode(property_type='getter')
    async def static(self):
        """是否静止"""
        #return await self._rpc.mpu_static()
        return self._state == 'static'

    @util.mode(property_type='getter')
    async def top_face(self):
        """哪一面朝上，当魔方静止时返回朝上一面的二维码的颜色，非静止时返回 `None` """
        if self._state != 'static':
            return None
        acc = await self._rpc.mpu_acc()
        comp, j = abs(acc[0]), 0
        for i in range(1, 3):
            if comp < abs(acc[i]):
                comp, j = abs(acc[i]), i
        return self._dir2color[('-' if acc[j]>0 else '+') + chr(88+j)]


class Cube(AioCube):
    """魔方的同步模式

    :param serial_or_ip: 要连接的 魔方的 IP 地址或序列号
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        super(Cube, self).__init__(serial_or_ip)
        self._mode = 'sync'

    def _in_event_loop(self):
        return self._event_thread == threading.current_thread()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.disconnect()

    def connect(self):
        """连接 魔方"""
        self._lo = asyncio.new_event_loop()
        self._event_thread = threading.Thread(target=self._run_loop, args=(self._lo,), daemon=True)
        self._event_thread.start()
        asyncio.run_coroutine_threadsafe(AioCube.connect(self), self._lo).result()

    def disconnect(self):
        """断开 魔方的连接"""
        asyncio.run_coroutine_threadsafe(AioCube.disconnect(self), self._lo).result()
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


class AsyncCube(Cube):
    """魔方的异步 (concurrent.futures.Future) 模式

    :param serial_or_ip: 要连接的 魔方的 IP 地址或序列号
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        super(AsyncCube, self).__init__(serial_or_ip)
        self._mode = 'async'


