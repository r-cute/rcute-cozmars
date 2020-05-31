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

    def _run_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._done_ev = asyncio.Event()
        loop.run_until_complete(self._done_ev.wait())
        to_cancel = []
        for t in asyncio.all_tasks():
            if asyncio.current_task() is not t:
                t.cancel()
                to_cancel.append(t)
        loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))
        asyncio.set_event_loop(None)
        loop.close()

    def __enter__(self):
        self._loop_thread = threading.Thread(target=self._run_loop)
        self._loop_thread.start()
        return mode(True)(AioRobot.__aenter__)(self)

    def __exit__(self, exc_type, exc, tb):
        asyncio.call_soon_threadsafe(self._done_ev.set)
        self._loop_thread.join(timeout=5)
        return mode(True)(AioRobot.__aexit__)(self, exc_type, exc, tb)

class AsyncRobot(Robot):
    def __init__(self, serial=None, ip=None):
        Robot.__init__(self, serial, ip)
        self._mode = 'async'


