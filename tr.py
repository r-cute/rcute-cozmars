import client,asyncio
async def main():
    async with client.robot.AioRobot(ip='192.168.1.100') as r:
        await r.screen.fill((1,1,100))
        await r.screen.brightness(.3)

        await asyncio.sleep(1)
asyncio.run(main())

