from rcute_cozmars import Robot
import cv2

# replace ip address with your cozmars' ip
with Robot('192.168.1.102') as robot:
    with robot.camera:

        print('Press ESC to stop')
        for frame in robot.camera.output_stream:
            cv2.imshow('cozmars camera', frame)
            if cv2.waitKey(1 ) == 27:
                break

cv2.destroyAllWindows()
