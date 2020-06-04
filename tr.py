import client,asyncio,functools,time
# async def main():
#     async with client.robot.AioRobot(ip='192.168.1.100') as r:
#         await r.screen.fill((1,1,100))
#         await r.screen.brightness(.3)
#         print(await r.screen.brightness())
#         await asyncio.sleep(1)
# asyncio.run(main())

with client.robot.Robot(ip='192.168.1.100') as r:
    r.screen.set_brightness(1,duration=1)
    r.screen.fill((100,0,0))
    r.button.when_pressed = lambda: print('pressed')
    r.button.when_released = lambda:print('relesase')
    r.sonar.when_in_range=lambda x:print(x)
    time.sleep(10)

# def mode(sync=False,pro=False):
#     def deco(func):
#         @functools.wraps(func)
#         def return_func(*args, **kwargs):
#             return func(*args, **kwargs)
#         return property(return_func).setter(return_func) if pro else return_func
#     return deco
# class A:
#     def __init__(s):
#         s.mode=1
#         s._a=4
#     @mode()
#     def o(s,a=None):
#         if a:
#             print('set')
#             s._a=a
#         else:
#             print('get')
#             return s._a

# a=A()
# a.o(34)
# print(a.o())

# async def main(a):
#     return await asyncio.sleep(3) if a else await asyncio.sleep(1)

# asyncio.run(main(0))