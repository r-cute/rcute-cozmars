import asyncio
import threading
from .util import mode
from .connection import Connection
from .screen import Screen

class AioRobot:
    def __init__(self, serial=None, ip=None):
        self._conn = Connection(self, serial, ip)
        self._mode = 'aio'
        self._screen = Screen(self)

    @property
    def screen(self):
        return self._screen

    @property
    def connection(self):
        return self._conn

    async def __aenter__(self):
        await self.connection.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.connection.disconnect()

    @mode()
    async def poweroff(self):
        await self.connection._get('/poweroff')

    @mode()
    async def reboot(self):
        await self.connection._get('reboot')

class Robot(AioRobot):
    def __init__(self, serial=None, ip=None):
        AioRobot.__init__(self, serial, ip)
        self._mode = 'sync'

    def __enter__(self):
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._run_loop, args=(self._loop))
        self._loop_thread.start()
        return mode(True)(AioRobot.__aenter__)(self)

    def __exit__(self, exc_type, exc, tb):
        mode(True)(AioRobot.__aexit__)(self, exc_type, exc, tb)
        asyncio.call_soon_threadsafe(self._done_ev.set)
        self._loop_thread.join(timeout=5)

    def _run_loop(self, loop):
        asyncio.set_event_loop(loop)
        self._done_ev = asyncio.Event()
        loop.run_until_complete(self._done_ev.wait())
        asyncio.gather(*asyncio.all_tasks()).cancel()
        asyncio.set_event_loop(None)
        loop.stop()
        loop.close()

class AsyncRobot(Robot):
    def __init__(self, serial=None, ip=None):
        Robot.__init__(self, serial, ip)
        self._mode = 'async'


