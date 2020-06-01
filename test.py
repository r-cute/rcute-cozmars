from threading import Thread
import asyncio
import time


def more_work(x):
    print("More work %s" % x)
    time.sleep(x)
    print("Finished more work %s" % x)
async def do_some_work(x):
    print("Waiting " + str(x))
    await asyncio.sleep(x)
    print('done wating', x)

def start_loop(loop):
    asyncio.set_event_loop(loop)
    try:
        # loop.run_forever()
        loop.run_until_complete(do_some_work(7))
    except Exception as e:
        print(type(e), e)
    finally:
        # for t in asyncio.all_tasks():
        #     t.cancle()
        async def cancel_all():
            asyncio.gather(*asyncio.all_tasks()).cancel()
        asyncio.run_coroutine_threadsafe(cancel_all(),loop)
        time.sleep(2)
        loop.stop()
        loop.close()
        print('cancelled')
        asyncio.set_event_loop(None)

new_loop = asyncio.new_event_loop()
t = Thread(target=start_loop, args=(new_loop,))
t.start()



# new_loop.call_soon_threadsafe(more_work, 6)
# new_loop.call_soon_threadsafe(more_work, 3)
asyncio.run_coroutine_threadsafe(do_some_work(5), new_loop)
asyncio.run_coroutine_threadsafe(do_some_work(2), new_loop)