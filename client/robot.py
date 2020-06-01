import asyncio
import aiohttp
import websockets
import threading
from .wsmprpc import RPCClient
from .util import mode
from .screen import Screen
from .camera import Camera

class AioRobot:
    def __init__(self, serial=None, ip=None):
        if not (serial or ip):
            raise error.CozmarsError('Neither serial number nor IP is provided')
        self._ip = ip
        self._serial = serial
        self._mode = 'aio'
        self._connected = False
        self._screen = Screen(self)
        self._camera = Camera(self, (320, 240), 10)

    @property
    def screen(self):
        return self._screen

    @property
    def camera(self):
        return self._camera

    @property
    def connected(self):
        return self._connected

    async def connect(self):
        if not self._connected:
            self._ws = await websockets.connect(f'ws://{self.host}/rpc')
            self._stub = RPCClient(self._ws)
            self._connected = True
            self._ip = self._ip or await self._get('/ip')
            self._serial = self._serial or await self._get('/serial')

    async def disconnect(self):
        if self._connected:
            await self._ws.close()
            self._connected = False

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    @property
    def host(self):
        return self._ip or f'rcute-{self._serial}.local'

    @property
    def ip(self):
        return self._ip

    @property
    def serial(self):
        return self._serial

    @mode()
    async def poweroff(self):
        await self._get('/poweroff')

    @mode()
    async def reboot(self):
        await self._get('/reboot')

    async def _get(self, sub_url):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://' + self.host + sub_url) as resp:
                return await resp.text()

class Robot(AioRobot):
    def __init__(self, serial=None, ip=None):
        AioRobot.__init__(self, serial, ip)
        self._mode = 'sync'

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.disconnect()

    def connect(self):
        self._loop = asyncio.new_event_loop()
        self._event_thread = threading.Thread(target=self._run_loop, args=(self._loop,))
        self._event_thread.start()
        asyncio.run_coroutine_threadsafe(AioRobot.connect(self), self._loop).result()
        return self

    def disconnect(self):
        asyncio.run_coroutine_threadsafe(AioRobot.disconnect(self), self._loop).result()
        self._loop.call_soon_threadsafe(self._done_ev.set)
        self._event_thread.join(timeout=5)

    def _run_loop(self, loop):
        asyncio.set_event_loop(loop)
        self._done_ev = asyncio.Event()
        loop.run_until_complete(self._done_ev.wait())
        tasks = asyncio.all_tasks(loop)
        for t in tasks:
            t.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.stop()
        loop.close()
        asyncio.set_event_loop(None)

class AsyncRobot(Robot):
    def __init__(self, serial=None, ip=None):
        Robot.__init__(self, serial, ip)
        self._mode = 'async'


