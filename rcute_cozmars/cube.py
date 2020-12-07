import asyncio
import aiohttp
import websockets
import threading
import logging
import json
from wsmprpc import RPCClient, RPCStream
from. import util

logger = logging.getLogger("rcute-cube")

class AioCube:
    """Asynchronous (async/await) mode of Cube

    :param serial_or_ip: The IP address or serial number of the Rubik's Cube to be connected
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        self._host ='rcute-cube-' + serial_or_ip +'.local' if len(serial_or_ip) == 4 else serial_or_ip
        self._mode ='aio'
        self._state ='moved'
        self._connected = False
        self._dir2color = {'+X':'red','-X':'green','+Y':'blue','-Y':'yellow','+Z':'white', '-Z':'orange'}
        self.last_action = None
        """The last action of the Rubik's Cube"""
        self.when_flipped = None
        """Callback function, called when the Rubik's Cube is flipped (with a direction parameter to indicate 90 degrees flip or 180 degrees), the default is `None` """
        self.when_shaked = None
        """Callback function, called when the Rubik's Cube is shaken, the default is `None` """
        self.when_rotated = None
        """Callback function, called when the cube is rotated horizontally (with a direction parameter indicating clockwise or counterclockwise), the default is `None` """
        self.when_pushed = None
        """Callback function, called when the cube is translated (with a direction parameter to indicate the direction of movement), the default is `None` """
        self.when_tilted = None
        """Callback function, called when the cube is tilted (with a direction parameter to indicate the direction of movement), the default is `None` """
        self.when_tapped = None
        """Callback function, called when tapping the Rubik's Cube, the default is `None` """
        self.when_fall = None
        """Callback function, called when the Rubik's Cube loses weight/free fall, the default is `None` """
        self.when_moved = None
        """Callback function, called when the cube is moved (including the above actions), the default is `None` """
        self.when_static = None
        """Callback function, called when the Rubik's Cube comes to rest, the default is `None` """


    def _in_event_loop(self):
        return True

    async def connect(self):
        """Establish a connection with the Rubik's Cube"""
        if not self._connected:
            self._ws = await websockets.connect(f'ws://{self._host}:81')
            if'-1' == await self._ws.recv():
                raise RuntimeError('Cannot connect to Rubik's Cube, please close other programs that are connecting Rubik's Cube')
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
            if self._mode =='aio':
                (await cb(*args)) if asyncio.iscoroutinefunction(cb) else cb(*args)
            else:
                self._lo.run_in_executor(None, cb, *args)

    async def _get_event(self):
        self._event_rpc = self._rpc.mpu_event()
        async for event in self._event_rpc:
            try:
                arg = self._dir2color.get(event[1], event[1])
                if event[0] in ('static','moved'):
                    self._state = event[0]
                else:
                    self.last_action = event[0], arg
                if event[0] in ('static','moved','fall','tapped','shaked'):
                    await self._call_callback(getattr(self,'when_'+event[0]))
                else:
                    await self._call_callback(getattr(self,'when_'+event[0]), arg)
            except Exception as e:
                logger.exception(e)

    @property
    def connected(self):
        """Whether connected to the Rubik's Cube"""
        return self._connected

    async def disconnect(self):
        """Disconnect from Rubik's Cube"""
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
        """Magic's Cube's IP Address"""
        return self._ip

    @property
    def hostname(self):
        """The Cube's URL"""
        return self._hostname

    @property
    def firmware_version(self):
        """The firmware version of the Rubik's Cube"""
        return self._firmware_version

    @property
    def mac(self):
        """Magic's Cube's MAC Address"""
        return self._mac

    @property
    def serial(self):
        """Serial Number of Rubik's Cube"""
        return self._serial

    async def _get(self, sub_url):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://' + self._host + sub_url) as resp:
                return await resp.text()

    @util.mode(property_type='setter')
    async def color(self, *args):
        """BGR color of LED light"""
        if args:
            await self._rpc.rgb(*(util.bgr(args[0]) if args[0] is not None else (0,0,0))[::-1])
        else:
            return (await self._rpc.rgb())[::-1]

    @util.mode(property_type='getter')
    async def acc(self):
        """Acceleration loss, when the Rubik's Cube is stationary, the acceleration is equal to the acceleration of gravity (but in fact there is an error)"""
        return await self._rpc.mpu_acc()

    @util.mode(property_type='getter')
    async def static(self):
        """Is it still"""
        #return await self._rpc.mpu_static()
        return self._state =='static'

    @util.mode(property_type='getter')  
    async def top_face(self):
        """Which side is up, when the Rubik’s Cube is stationary, it returns to the color of the QR code on the upside, and returns to `None` """
        if self._state !='static':
            return None
        acc = await self._rpc.mpu_acc()
        comp, j = abs(acc[0]), 0
        for i in range(1, 3):
            if comp <abs(acc[i]):
                comp, j = abs(acc[i]), i
        return self._dir2color[('-' if acc[j]>0 else'+') + chr(88+j)]


class Cube(AioCube):
    """The synchronization mode of Rubik's Cube
    :param serial_or_ip: The IP address or serial number of the Rubik's Cube to be connected
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        super(Cube, self).__init__(serial_or_ip)
        self._mode ='sync'

    def _in_event_loop(self):
        return self._event_thread == threading.current_thread()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.disconnect()

    def connect(self):
        """Connect Rubik's Cube"""
        self._lo = asyncio.new_event_loop()
        self._event_thread = threading.Thread(target=self._run_loop, args=(self._lo,), daemon=True)
        self._event_thread.start()
        asyncio.run_coroutine_threadsafe(AioCube.connect(self), self._lo).result()

    def disconnect(self):
        """Disconnect the Rubik's Cube"""
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
    """Asynchronous (concurrent.futures.Future) mode of Rubik's Cube

    :param serial_or_ip: The IP address or serial number of the Rubik's Cube to be connected
    :type serial_or_ip: str
    """
    def __init__(self, serial_or_ip):
        super(AsyncCube, self).__init__(serial_or_ip)
        self._mode ='async'