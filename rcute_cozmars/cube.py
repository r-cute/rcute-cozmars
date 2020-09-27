
import asyncio
import aiohttp
import websockets
import threading
import logging
import json
from wsmprpc import RPCClient, RPCStream
from . import util

logger = logging.getLogger("rcute-魔方")

class Aio魔方:
    """魔方的异步 (async/await) 模式

    :param serial_or_ip: 要连接的 魔方的 IP 地址或序列号
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        self._host = 'rcute-魔方-' serial_or_ip + '.local' if len(serial_or_ip) == 4 else serial_or_ip
        self._mode = 'aio'
        self._connected = False
        """回调函数，当魔方被翻转90度时调用，默认为 `None` """
        self.when_flipped_90 = None
        """回调函数，当魔方被翻转180度时调用，默认为 `None` """
        self.when_flipped_180 = None
        """回调函数，当魔方被晃动时调用，默认为 `None` """
        self.when_shaked = None
        """回调函数，当魔方被水平旋转时调用，默认为 `None` """
        self.when_rotated = None
        """回调函数，当魔方被水平挪动时调用，默认为 `None` """
        self.when_moved = None

    def _in_event_loop(self):
        return True

    async def connect(self):
        """建立与魔方的连接"""
        if not self._connected:
            self._ws = await websockets.connect(f'ws://{self._host}:81')
            if '-1' == await self._ws.recv():
                raise RuntimeError('无法连接 魔方, 请先关闭其他已经连接 魔方的程序')
            self._rpc = RPCClient(self._ws)
            about = json.loads(await self._get('/about'))
            self._ip = about['ip']
            self._serial = about['serial']
            self._firmware_version = about['version']
            self._hostname = about['hostname']
            self._event_task = asyncio.create_task(self._get_event)
            self._connected = True

    async def _call_callback(self, cb, *args):
        if cb:
            if self._mode == 'aio':
                (await cb(*args)) if asyncio.iscoroutinefunction(cb) else cb(*args)
            else:
                self._lo.run_in_executor(None, cb, *args)

    async def _get_event(self):
        self._event_rpc = self._rpc.mpu_stream()
        async for event, data in self._event_rpc:
            try:
                if event == 'flipped90':
                    await self._call_callback(self.when_flipped_90)
                elif event == 'flipped180':
                    await self._call_callback(self.when_flipped_180)
                elif event == 'rotated':
                    await self._call_callback(self.when_rotated, data)
                elif event == 'moved':
                    await self._call_callback(self.when_moved, data)
                elif event == 'shaked':
                    await self._call_callback(self.when_shaked)
            except Excpetion as e:
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
    def serial(self):
        """魔方的序列号"""
        return self._serial

    async def _get(self, sub_url):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://' + self._host + sub_url) as resp:
                return await resp.text()

    @util.mode(property_type='setter')
    async def color(self, *args):
    """LED 灯的 RGB 颜色"""
        return await self._rpc.rgb(*args)

    @util.mode(property_type='getter')
    async def acceleration(self):
    """加速度失量"""
        return await self._rpc.accel()

class 魔方(Aio魔方):
    """魔方的同步模式

    :param serial_or_ip: 要连接的 魔方的 IP 地址或序列号
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        super(魔方, self).__init__(serial_or_ip)
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
        asyncio.run_coroutine_threadsafe(AioRobot.connect(self), self._lo).result()

    def disconnect(self):
        """断开 魔方的连接"""
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


class Async魔方(魔方):
    """魔方的异步 (concurrent.futures.Future) 模式

    :param serial_or_ip: 要连接的 魔方的 IP 地址或序列号
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        super(Async魔方, self).__init__(serial_or_ip)
        self._mode = 'async'


