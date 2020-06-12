import cozmars
import cv2

with cozmars.Robot(ip='192.168.1.105') as robot:
    with robot.camera:

        print('Press ESC to stop')
        for frame in robot.camera.output_stream:
            cv2.imshow('cozmars camera', frame)
            if cv2.waitKey(1 ) == 27:
                break

cv2.destroyAllWindows()
