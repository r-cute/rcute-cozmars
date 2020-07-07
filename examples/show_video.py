from rcute_cozmars import Robot
import cv2

# 把以下 IP 地址换成你的 Cozmars 的 IP 地址
with Robot('192.168.1.102') as robot:

    with robot.camera:

        print('按下任意键退出')
        for frame in robot.camera.output_stream:

            cv2.imshow('cozmars camera', frame)
            if cv2.waitKey(1) > 0:
                break

cv2.destroyAllWindows()
