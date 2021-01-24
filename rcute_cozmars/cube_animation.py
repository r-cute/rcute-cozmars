# these animations are hard coded for 15r/m motors
import asyncio
import numpy as np
import cv2
from .aruco import ArucoDetector

def cube_id(id):
    return 0<= id<= 6

def charger_id(id):
    return id == 0

def exe(rec, image, id_filter, win):
    corners, ids = rec.detect(image)
    if win:
        rec.draw_labels(image, corners, ids)
        cv2.imshow(win, image)
        cv2.waitKey(1)
    if ids is not None:
        for corner, id in zip(corners, ids):
            if id_filter(id[0]):
                return corner.reshape(-1,2), id[0]
    return None, None

async def detect_and_imshow(cam_buf, rec, id_filter, win=None):
    image = await cam_buf.read()
    return await asyncio.get_running_loop().run_in_executor(None, exe, rec, image, id_filter, win)

async def search_for_cube(robot, cam_buf=None, clockwise=True, reverse=2, rec=None, id_filter=cube_id, show_view=False):
    rec = rec or ArucoDetector()
    if type(show_view) != str:
        show_view = show_view and 'search_for_cube'
    await robot.lift.height(0)
    await robot.head.angle(-15)
    try:
        cam = cam_buf or robot.camera.get_buffer()
        not cam_buf and (await cam.open())
        for _ in range(5):
            await cam.read() # let's discard the first few frames
        count = 0
        while True:
            corner, id= await detect_and_imshow(cam, rec, id_filter, show_view)
            if corner is not None:
                return corner, id
            if count < reverse:
                await robot.motor.set_speed((-.5, .5) if clockwise else (.5, -.5), 0.1)
            else:
                await robot.motor.set_speed((.5, -.5) if clockwise else (-.5, .5), 0.35 if count ==reverse else 0.1)
            count += 1
            await asyncio.sleep(.4)
    finally:
        not cam_buf and (await cam.close())

async def center_cube(robot, cam_buf=None, rec=None, id_filter=cube_id, show_view=False):
    rec = rec or ArucoDetector()
    if type(show_view) != str:
        show_view = show_view and 'center_cube'
    mid = [a/2 for a in robot.camera.resolution]
    # mid[0] += 40#offset
    try:
        cam = cam_buf or robot.camera.get_buffer()
        not cam_buf and (await cam.open())

        while True:
            corner, id= await detect_and_imshow(cam, rec, id_filter, show_view)
            if corner is None:
                return corner, id
            else:
                av = np.average(corner, axis=0)
                x, y = [av[i] - mid[i] for i in range(2)]
                e = np.average(rec.edges(corner))
                if not -70 < x < 70:
                    sp = np.clip(.02*((x-50) if x >=50 else (50+x)), -.2, .2)
                    await robot.motor.set_speed((sp, -sp), max((100-e)/130, .1))
                elif e < 50:
                    await robot.forward(max(.35, (50-e)/20))
                elif e > 60:
                    await robot.backward(max(.35, (e-60)/25))
                else:
                    return corner, id
                await asyncio.sleep(.4)
    finally:
        not cam_buf and (await cam.close())

async def aim_at_cube(robot, corner, rec=None):
    rec = rec or ArucoDetector()
    tr, br, bl, tl = rec.order4points(corner)
    top = int(np.linalg.norm(tr - tl))
    right = int(np.linalg.norm(tr - br))
    left = int(np.linalg.norm(tl - bl))
    vertical = max(left, right)
    ratio = top / vertical
    if ratio < .9:
        await getattr(robot, 'turn_left' if left<right else 'turn_right')(1.5*ratio*65/vertical)
        await asyncio.sleep(.2)
        a = max((100-vertical)*(1-ratio)*.4, .5)
        await robot.forward(a)
        await asyncio.sleep(.2)
        await getattr(robot, 'turn_left' if left>=right else 'turn_right')(8*(1-ratio)*90/vertical)
        return left < right

async def dock_with_cube(robot, cam_buf=None, rec=None, id_filter=cube_id, show_view=False):
    if type(show_view) != str:
        show_view = show_view and 'dock_with_cube'
    await robot.lift.height(0)
    offset = await robot.env.get('cube_center_offset')
    rec = rec or ArucoDetector()
    mid = robot.camera.resolution[0] /2 + offset
    delay = 1 / robot.camera.frame_rate
    count = 0
    try:
        cam = cam_buf or robot.camera.get_buffer()
        not cam_buf and (await cam.open())

        sp = 1, 1
        while True:
            corner, id = await detect_and_imshow(cam, rec, id_filter, show_view)
            dist = await robot.sonar.distance()
            if dist <= .06:
                count += delay
            else:
                count = 0
            if count > 2:
                await robot.motor.stop()
                break
            if corner is not None:
                x = np.average(corner, axis=0)[0] - mid
                if x > 10:
                    sp = 1, max(1-(x-10)/10, 0.1)
                elif x < -10:
                    sp = max(1-(-x-10)/10, 0.1), 1
                else:
                    sp = 1, 1
                if dist < .1:
                    sp = tuple(s*dist/.1 for s in sp)
            elif dist < .1:
                sp = dist/.1, dist/.1
            await robot.motor.speed(tuple(a*.7 for a in sp))
    finally:
        not cam_buf and (await cam.close())

async def pick_up_cube(robot, height=1, retry=3, id_filter=cube_id, show_view=False):
    rec = ArucoDetector()
    show_view = show_view and 'pick_up_cube'
    async with robot.camera.get_buffer() as buf:
        clockwise, reverse = True, 2
        while True:
            corner, id = await animations['search_for_cube'](robot, buf, clockwise=clockwise, reverse=reverse, rec=rec, id_filter=id_filter, show_view=show_view)
            if corner is None:
                return
            corner, id = await animations['center_cube'](robot, buf, rec=rec, id_filter=id_filter, show_view=show_view)
            if corner is None:
                reverse = 2
                continue
            clockwise = await animations['aim_at_cube'](robot, corner, rec=rec)
            if clockwise is not None:
                reverse = 0
                continue
            await animations['dock_with_cube'](robot, buf, rec=rec, id_filter=id_filter, show_view=show_view)
            await robot.lift.height(height)
            await asyncio.sleep(.5)
            if (await robot.sonar.distance()) > .06:
                return True
            elif retry:
                await robot.backward(2)
                return await pick_up_cube(robot, height, retry-1, id_filter, show_view)
            else:
                return False
'''
async def search_for_charger(robot, cam_buf=None, clockwise=True, reverse=2, rec=None, show_view=False):
    if type(show_view) != str:
        show_view = 'search_for_charger'
    await search_for_cube(robot, cam_buf=cam_buf, rec=rec, id_filter=charger_id, show_view=show_view)

async def approach_charger(robot, cam_buf=None, rec=None, id_filter=charger_id, show_view=False): # similar to dock_with_cube
    if type(show_view) != str:
        show_view = show_view and 'approach_charger'
    await robot.lift.height(0)
    offset = await robot.env.get('cube_center_offset')
    rec = rec or ArucoDetector()
    mid = robot.camera.resolution[0] /2 + offset
    try:
        cam = cam_buf or robot.camera.get_buffer()
        not cam_buf and (await cam.open())

        sp = 1, 1
        while True:
            corner, id = await detect_and_imshow(cam, rec, id_filter, show_view)
            if corner is not None:
                e = np.average(rec.edges(corner))
                if e >72:
                    await robot.motor.speed(0)
                    return corner
                x = np.average(corner, axis=0)[0] - mid
                if x > 10:
                    sp = 1, max(1-(x-10)/10, 0.1)
                elif x < -10:
                    sp = max(1-(-x-10)/10, 0.1), 1
                else:
                    sp = .5, .5
            await robot.motor.speed(sp)
    finally:
        not cam_buf and (await cam.close())

async def dock_with_charger(robot, corner, rec=None):
    rec = rec or ArucoDetector()
    tr, br, bl, tl = rec.order4points(corner)
    right = int(np.linalg.norm(tr - br))
    left = int(np.linalg.norm(tl - bl))
    ratio = left / right
    if ratio < 1:
        await robot.turn_left(5 + 5*(ratio-1))
    else:
        await robot.turn_right(5 + 5*(1-ratio))
    await robot.motor.speed(-.5)
    count = 0
    while True:
        await asyncio.sleep(1)
        count += 1
        if 0 in robot.infrared.state:# == (0, 0):
            await robot.motor.set_speed(.5, .1)
            return True
        if count >5:
            await robot.motor.speed(0)
            return False

async def drive_on_charger(robot, show_view=False):
    rec = ArucoDetector()
    show_view = show_view and 'drive_on_charger'
    async with robot.camera.get_buffer() as buf:
        clockwise, reverse = True, 2
        while True:
            corner, id = await animations['search_for_cube'](robot, buf, clockwise=clockwise, reverse=reverse, rec=rec, id_filter=charger_id, show_view=show_view)
            if corner is None:
                return
            corner, id = await animations['center_cube'](robot, buf, rec=rec, id_filter=charger_id, show_view=show_view)
            if corner is None:
                reverse = 2
                continue
            clockwise = await animations['aim_at_cube'](robot, corner, rec=rec)
            if clockwise is not None:
                reverse = 0
                continue
            corner = await animations['approach_charger'](robot, buf, rec=rec, show_view=show_view)
            return await animations['dock_with_charger'](robot, corner, rec=rec)
'''

animations = {'search_for_cube': search_for_cube,
    'center_cube': center_cube,
    'aim_at_cube': aim_at_cube,
    'dock_with_cube': dock_with_cube,
    'pick_up_cube': pick_up_cube,
    # 'search_for_charger': search_for_charger,
    # 'approach_charger': approach_charger,
    # 'drive_on_charger': drive_on_charger,
    # 'dock_with_charger': dock_with_charger,
    }
