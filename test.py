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
    global done_ev
    asyncio.set_event_loop(loop)

    done_ev=asyncio.Event()
    try:
        # loop.run_forever()
        loop.run_until_complete(done_ev.wait())
    except Exception as e:
        print('complete', type(e), e)
    finally:
        tasks = asyncio.all_tasks(loop)
        print('len',len(tasks))
        for t in tasks:
            t.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.stop()
        loop.close()
        print('cancelled')
        asyncio.set_event_loop(None)


loop = asyncio.new_event_loop()
t = Thread(target=start_loop,args=(loop,))
t.start()



# new_loop.call_soon_threadsafe(more_work, 6)
# new_loop.call_soon_threadsafe(more_work, 3)

asyncio.run_coroutine_threadsafe(do_some_work(5), loop)
asyncio.run_coroutine_threadsafe(do_some_work(2), loop)
time.sleep(2)
# loop.call_soon_threadsafe(done_ev.set)
done_ev.set()
t.join()