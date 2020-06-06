import client,asyncio,functools,time
import asyncio

async def run():
    proc = await asyncio.create_subprocess_shell('sudo python3.8 -m pip install sanic -U', stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)

    async def write(stream, bb):
        while True:
            line = await stream.readline()
            if line:
                print(bb,line)
            else:
                break
    await asyncio.wait([write(proc.stdout,'[out]'), write(proc.stderr,'[err]')])

asyncio.run(run())
# async def main():
#     async with client.robot.AioRobot(ip='192.168.1.100') as r:
#         await r.forward(3)

# asyncio.run(main())
# async def f():
#     print('fff')
# with client.robot.AsyncRobot(ip='192.168.1.100') as r:

#     time.sleep(5)
#     r.forward(3).result()

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