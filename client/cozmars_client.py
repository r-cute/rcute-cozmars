import asyncio, websockets
from wsmprpc import RPCClient, RPCStream
import cv2, numpy as np
import sounddevice as sd, soundfile as sf


async def main():

    ws = await websockets.connect('ws://192.168.1.100:80/rpc')
    stub = RPCClient(ws)
    # print(await stub.rec_vol())

    # with sf.SoundFile('file.wav', mode='x', samplerate=16000,
    #               channels=1, subtype='PCM_24') as file:
    #     async for d in stub.mic(2):
    #         file.write(np.frombuffer(d, dtype='int16'))

    # print(await stub.distance_threshold())
    # async for a in stub.sensor_data(request_stream=[]):
    #     print(a)

    # async def gen(s):
    #     async for a in s:
    #         yield a
    await stub.backlight(.5)
    await stub.fill((255,0,0))
    stream=RPCStream()
    tone=stub.tone(request_stream=stream)
    async def play_tone():
        nonlocal stream
        for a in ['A4','B4',None,StopAsyncIteration()]:
            await stream.put(a)
            await asyncio.sleep(1)
    asyncio.create_task(play_tone())
    await tone
    await ws.close()




asyncio.run(main())

