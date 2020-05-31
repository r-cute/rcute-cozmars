import client
import asyncio
async def main():
    async with client.robot.AioRobot(ip="192.168.1.100") as r:
        await r.screen.set_backlight(0.5)
        await r.screen.fill((0,0,100))

        await asyncio.sleep(1)


# e=asyncio.Event()
# l=asyncio.new_event_loop()
# asyncio.set_event_loop(l)
# async def mm():
#     asyncio.create_task(asyncio.sleep(10))
#     await asyncio.sleep(3)
# fut=asyncio.run_coroutine_threadsafe(main(), l)

# async def c():
#     b=[]
#     for t in asyncio.all_tasks():
#         if t is asyncio.current_task():
#             continue
#         # t.cancel()
#         b.append(t)

#     await asyncio.gather(*b, return_exceptions=True)
# l.run_until_complete(c())
# fut.result()
# asyncio.set_event_loop(None)
# l.close()



import time

with client.robot.Robot(ip='192.168.1.100') as r:
    r.screen.set_backlight(.4)
    r.screen.fill((0,100,0))
    time.sleep(1)
