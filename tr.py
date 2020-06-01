import client
import time
with client.robot.AsyncRobot(ip='192.168.1.100') as r:
    r.screen.fill((100,0,0)).result()
    print(r.screen.set_backlight(.4).result())
    time.sleep(2)
