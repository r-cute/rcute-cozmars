传感器
============

机器人还要能感知周围的环境，光会动只是机器。

这一节先介绍 Cozmars 身上的三个简单的传感器：背上的按钮 :data:`button` 、前头的超声波距离传感器 :data:`sonar` ，和底部的两个红外传感器 :data:`infrared`


.. code:: python

    from rcute_cozmars import Robot
    import time

    with Robot('192.168.1.102') as robot:
        while True:
            print(f'按钮状态：','按下' if robot.button.pressed else '松开')
            print(f'红外传感器状态：{robot.infrared.state}')
            print(f'前方障碍物距离：{robot.sonar.distance}米')
            print('............................')
            time.sleep(.3)



后面还会介绍另外两个传感器：摄像头和麦克风。别急，休息，休息一会儿~