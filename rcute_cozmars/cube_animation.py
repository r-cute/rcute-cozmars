import asyncio
import numpy as np
import cv2
from .qrcode import QRCodeRecognizer

def exe(rec, image, win):
    pts, text = rec.recognize(image)
    if win:
        rec.draw_labels(image, pts, text)
        cv2.imshow(win, image)
        cv2.waitKey(1)
    return pts, text

async def rec_and_imshow(cam_buf, rec, win=None):
    image = await cam_buf.read()
    return await asyncio.get_running_loop().run_in_executor(None, exe, rec, image, win)

async def search_for_cube(robot, cam_buf=None, clockwise=True, reverse=2, rec=None, debug=False):
    rec = rec or QRCodeRecognizer()
    await robot.head.angle(-15)
    cam = cam_buf or robot.camera.get_buffer()
    not cam_buf and (await cam.open())
    try:
        count = 0
        await cam.read()
        while True:
            pts, text= await rec_and_imshow(cam, rec, debug and 'search_for_cube')
            if pts is not None:
                if 'cube-' in text:
                    return pts, text
                elif text == '':
                    max_edge = max(rec.edges(pts))
                    if max_edge < 60:
                        await robot.forward((65-max_edge)/15)
                    for i in range(2):
                        await robot.head.angle(-15-10*(i%2))
                        await asyncio.sleep(.3)
                        pts, text= await rec_and_imshow(cam, rec, debug and 'search_for_cube')
                        if 'cube-' in text:
                            return pts, text
            if count < reverse:
                await robot.motor.set_speed((-.5, .5) if clockwise else (.5, -.5), 0.15)
            else:
                await robot.motor.set_speed((.5, -.5) if clockwise else (-.5, .5), 0.5 if count ==reverse else 0.15)
            count += 1
            await asyncio.sleep(.4)
    finally:
        not cam_buf and (await cam.close())

async def center_cube(robot, cam_buf=None, rec=None, debug=False):
    rec = rec or QRCodeRecognizer()
    cam = cam_buf or robot.camera.get_buffer()
    not cam_buf and (await cam.open())
    mid = [a/2 for a in robot.camera.resolution]
    try:
        while True:
            pts, text = await rec_and_imshow(cam, rec, debug and 'center_cube')
            if pts is None:
                return pts, text
            else:
                av = np.average(pts, axis=0)
                x, y = [av[i] - mid[i] for i in range(2)]
                e = np.average(rec.edges(pts))
                if not -65 < x < 65:
                    sp = np.clip(.02*((x-50) if x >=50 else (50+x)), -.5, .5)
                    await robot.motor.set_speed((sp, -sp), max((100-e)/100, .1))
                elif e < 60:
                    await robot.forward(max(.7, (60-e)/15))
                elif e > 70:
                    await robot.backward(max(.7, (e-70)/15))
                else:
                    return pts, text
                await asyncio.sleep(.4)
    finally:
        not cam_buf and (await cam.close())

async def aim_at_cube(robot, pts, rec=None, debug=False):
    rec = rec or QRCodeRecognizer()
    tr, br, bl, tl = rec.order4points(pts)
    top = int(np.linalg.norm(tr - tl))
    right = int(np.linalg.norm(tr - br))
    left = int(np.linalg.norm(tl - bl))
    vertical = max(left, right)
    ratio = top / vertical
    if ratio < .9:
        await getattr(robot, 'turn_left' if left<right else 'turn_right')(2*ratio*70/vertical)
        await asyncio.sleep(.2)
        a = max((100-vertical)*(1-ratio)*.8, 1.5)
        await robot.forward(a)
        await asyncio.sleep(.2)
        await getattr(robot, 'turn_left' if left>=right else 'turn_right')(10*(1-ratio)*80/vertical)
        return left < right
    return

async def dock_with_cube(robot, cam_buf, rec=None, debug=False):
    rec = rec or QRCodeRecognizer()
    cam = cam_buf or robot.camera.get_buffer()
    not cam_buf and (await cam.open())
    mid = robot.camera.resolution[0] /2
    delay = 1 / robot.camera.frame_rate
    count = 0
    try:
        sp = 1, 1
        while True:
            pts, text = await rec_and_imshow(cam, rec, debug and 'dock_with_cube')
            dist = await robot.sonar.distance()
            if dist <= .05:
                count += delay
            else:
                count = 0
            if count > 1.5:
                await robot.motor.stop()
                break
            if pts is not None:
                x = np.average(pts, axis=0)[0] - mid - 40
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
            await robot.motor.speed(sp)
    finally:
        not cam_buf and (await cam.close())

async def pick_up_cube(robot, height=1, retry=3, debug=False):
    rec = QRCodeRecognizer()
    await robot.lift.height(0)
    async with robot.camera.get_buffer() as buf:
        clockwise, reverse = True, 2
        while True:
            pts, text = await animations['search_for_cube'](robot, buf, clockwise=clockwise, reverse=reverse, rec=rec, debug=debug)
            if pts is None:
                return
            pts, text = await animations['center_cube'](robot, buf, rec=rec, debug=debug)
            if pts is None:
                reverse = 2
                continue
            clockwise = await animations['aim_at_cube'](robot, pts, rec=rec, debug=debug)
            if clockwise is not None:
                reverse = 0
                continue
            await animations['dock_with_cube'](robot, buf, rec=rec, debug=debug)
            await robot.lift.height(height)
            if (await robot.sonar.distance()) > .06:
                return True
            elif retry:
                await robot.backward(2)
                return await pick_up_cube(robot, height, retry-1, debug)
            else:
                return False

async def put_down_cube(robot, height=0):
    await robot.lift.height(height)
    await asyncio.sleep(1)
    await robot.backward(1)

animations = {'search_for_cube': search_for_cube,
    'center_cube': center_cube,
    'aim_at_cube': aim_at_cube,
    'dock_with_cube': dock_with_cube,
    'pick_up_cube': pick_up_cube,
    'put_down_cube': put_down_cube}
