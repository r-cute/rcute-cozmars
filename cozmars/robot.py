import asyncio
import aiohttp
import websockets
import threading
import logging
from wsmprpc import RPCClient, RPCStream
from . import error, util, screen, camera, microphone, button, sonar, infrared, lift, head, buzzer, motor

logger = logging.getLogger(__name__)

class AioRobot:
    def __init__(self, serial=None, ip=None):
        if not (serial or ip):
            raise error.CozmarsError('Neither serial number nor IP is provided')
        self._ip = ip
        self._serial = serial
        self._mode = 'aio'
        self._connected = False
        self._screen = screen.Screen(self)
        self._camera = camera.Camera(self, resolution=(480,360), framerate=5, q_size=5)
        self._microphone = microphone.Microphone(self, samplerate=16000, dtype='int16', q_size=5)
        self._button = button.Button(self)
        self._sonar = sonar.Sonar(self)
        self._infrared = infrared.Infrared(self)
        self._lift = lift.Lift(self)
        self._head = head.Head(self)
        self._buzzer = buzzer.Buzzer(self)
        self._motor = motor.Motor(self)

    @property
    def motor(self):
        return self._motor

    @property
    def head(self):
        return self._head

    @property
    def buzzer(self):
        return self._buzzer

    @property
    def lift(self):
        return self._lift

    @property
    def infrared(self):
        return self._infrared

    @property
    def button(self):
        return self._button

    @property
    def sonar(self):
        return self._sonar

    @property
    def screen(self):
        return self._screen

    @property
    def camera(self):
        return self._camera

    @property
    def microphone(self):
        return self._microphone

    @property
    def connected(self):
        return self._connected

    async def connect(self):
        if not self._connected:
            self._ws = await websockets.connect(f'ws://{self.host}/rpc')
            self._stub = RPCClient(self._ws)
            self._ip = self._ip or await self._get('/ip')
            self._serial = self._serial or await self._get('/serial')
            self._server_version = await self._get('/version')
            self._sensor_task = asyncio.create_task(self._get_sensor_data())
            self._connected = True

    async def _call_callback(self, cb, *args):
        if cb:
            if asyncio.iscoroutinefunction(cb):
                await cb(*args)
            else:
                cb(*args)

    async def _get_sensor_data(self):
        self._sensor_data_rpc = self._stub.sensor_data()
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
                    self.infrared._state = data ^ 1, self.infrared._state[1]
                    await self._call_callback(self.infrared.when_changed)
                elif event == 'rir':
                    self.infrared._state = self.infrared._state[0], data ^ 1
                    await self._call_callback(self.infrared.when_changed)
            except Exception as e:
                logger.exception(e)

    async def disconnect(self):
        if self._connected:
            self._sensor_task.cancel()
            self._sensor_data_rpc.cancel()
            # await self.camera._close()
            # await self.microphone._close()
            await self._ws.close()
            self._connected = False

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    @util.mode(force_sync=False)
    async def forward(self, duration=None):
        await self.motor.set_speed((1,1), duration)

    @util.mode(force_sync=False)
    async def backward(self, duration=None):
        await self.motor.set_speed((-1,-1), duration)

    @util.mode(force_sync=False)
    async def turn_left(self, duration=None):
        await self.motor.set_speed((-1,1), duration)

    @util.mode(force_sync=False)
    async def turn_right(self, duration=None):
        await self.motor.set_speed((1,-1), duration)

    @property
    def host(self):
        return self._ip or f'rcute-{self._serial}.local'

    @property
    def ip(self):
        return self._ip

    @property
    def server_version(self):
        return self._server_version

    @property
    def serial(self):
        return self._serial

    @util.mode()
    async def poweroff(self):
        await self._get('/poweroff')

    @util.mode()
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
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        asyncio.set_event_loop(None)

class AsyncRobot(Robot):
    def __init__(self, serial=None, ip=None):
        Robot.__init__(self, serial, ip)
        self._mode = 'async'


