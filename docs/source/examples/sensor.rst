传感器
============

机器人还要能感知周围的环境，光会动的只是机器

这一节先介绍 Cozmars 身上的三个简单的传感器：背上的按钮 :data:`button` 、前头的声纳 :data:`sonar` （超声波距离传感器），和底部的两个红外传感器 :data:`infrared`


这三个传感器各有一些属性用来查询其状态：

- 按钮 :data:`button` 有 :data:`pressed` ， :data:`held` ， :data:`double_pressed` 三个属性，分别表示按钮是否被按下、被长按和被双击
- 声纳 :data:`sonar` 通过超声波反射来判断前方障碍物的距离，其 :data:`distance` 属性用来查询前方障碍物的距离（米）
- 红外传感器 :data:`infrared` 自身能发出的红外光，并感应的红外反射的强弱。:data:`state` 属性是一个两元素组成的元组，分别表示左右两个传感器是否接收到红外反射，0 表示没有或反射很弱，1 表示有较强的反射


.. note::

    同马达 :data:`motor` 一样，两个红外传感器也在逻辑上被看成一个整体

查询传感器状态
----------------

以下程序每隔 0.3 秒查询一次传感器的状态。试试按动按钮，在小车前摆放障碍物，或者将小车拿起再放下，观察传感器状态的变化：

.. code:: python

    from rcute_cozmars import Robot
    import time

    with Robot('192.168.1.102') as robot:
        while True:
            print('按钮状态：','按下' if robot.button.pressed else '松开')
            print('红外传感器状态：', robot.infrared.state)
            print('前方障碍物距离：', robot.sonar.distance, '米')
            print('............................')
            time.sleep(.3)

以下程序通过不断查询声纳的状态，当前方障碍物距离小于 5 cm 时发出报警：

.. code:: python

    from rcute_cozmars import Robot
    import time

    with Robot('192.168.1.102') as robot:

        while True: # 不断循环，按 Ctrl + C 退出

            if robot.sonar.distance < 0.05:
                robot.buzzer.set_tone('C4', 1)

            time.sleep(.3)

回调函数
----------------

但上面的程序需要一遍遍地查询状态数据，显得很“费劲”

更好的办法是利用 :data:`sonar` 的 :data:`when_in_range` 属性设置一个回调函数，当前方有障碍物进入 :data:`threshold_distance` 范围内时，该函数就会被自动调用：

.. code:: python

    from rcute_cozmars import Robot
    from signal import pause

    with Robot('192.168.1.102') as robot:

        def ring(dist):
            robot.buzzer.set_tone('C4', 1)

        robot.sonar.threshold_distance = 0.05
        robot.sonar.when_in_range = ring

        pause() # 让程序在此暂停，按 Ctrl + C 退出


顾名思义，:data:`sonar.when_out_of_range` 是当前方有障碍物离开 :data:`threshold_distance` 范围时会被调用的函数

而通过 :data:`infrared.when_state_changed` 属性可以设置当红外传感器状态变换时被调用的函数，可以用来做经（无）典（聊）的寻迹小车实验：

.. code:: python

    from rcute_cozmars import Robot
    from signal import pause

    with Robot('192.168.1.102') as robot:

        def steer(state):
            print('红外传感器读数:', state)
            robot.motor.speed = state

        robot.infrared.when_state_changed = steer

        pause()



:data:`button` 的回调函数就更丰富了，有 :data:`when_pressed` 、:data:`when_released`、 :data:`when_held` 和 :data:`when_double_pressed` ，分别是当按钮被按下、被释放、被按住、被双击时的回调函数，这里就不一一演示了，请试着阅读以下相关的 API，自己测试一下！

.. seealso::

    `rcute_cozmars.button <../api/button.html>`_ ， `rcute_cozmars.sonar <../api/sonar.html>`_  ， `rcute_cozmars.infrared <../api/infrared.html>`_

后面还会介绍另外两个传感器：摄像头和麦克风。别急，休息，休息一会儿 ...