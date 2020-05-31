import asyncio
from concurrent import futures
import websockets
from .wsmprpc import RPCClient
from . import error
from .util import mode

class Connection:
    def __init__(self, robot, serial=None, ip=None):
        if not (serial or ip):
            raise error.CozmarsError('Neither serial number nor IP is provided')
        self._robot = robot
        self._ip = ip
        self._serial = serial
        self._connected = False

    @property
    def _mode(self):
        return self._robot._mode

    @property
    def connected(self):
        return self._connected

    @mode()
    async def connect(self):
        if not self._connected:
            self._ws = await websockets.connect(f'ws://{self.host}/rpc')
            self._client = RPCClient(self._ws)
            self._connected = True

    @property
    def host(self):
        return self._ip or f'rcute-{self._serial}.local'

    @mode()
    async def ip(self):
        if not self._ip:
            self._ip = await self._get(f'http://{self.host}/ip')
        return self._ip

    @mode()
    async def serial(self):
        if not self._serial:
            self._serial = await self._get(f'http://{self.host}/serial')
        return self._serial

    @property
    def rpc(self):
        return self._client

    @mode()
    async def disconnect(self):
        if self._connected:
            await self._ws.close()
            self._connected = False

    async def _get(sub_url):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get('http://' + self.host + sub_url) as resp:
                return await resp.text()

    def _run_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._done_ev = asyncio.Event()
        loop.run_until_complete(self._done_ev.wait)
        to_cancel = []
        for t in asyncio.all_tasks():
            if asyncio.current_task() is not t:
                t.cancel()
                to_cancel.append(t)
        loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))
        asyncio.set_event_loop(None)
        loop.close()



