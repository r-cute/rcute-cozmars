传感器与回调函数
=================

机器人还应该能感知周围的环境，如果会动的那叫机器

这一节先介绍 Cozmars 身上的三个简单的传感器：背上的触摸传感器 :data:`touch_sensor` 、前头的声纳（超声波距离传感器）:data:`sonar` ，和底部的两个红外传感器 :data:`ir_sensors`


这三个传感器各有一些属性用来查询其状态：

- 按钮 :data:`touch_sensor` 有 :data:`touched` ， :data:`long_touched` ， :data:`double_touched` 三个属性，分别表示按钮是否被按下、被长按和被双击
- 声纳 :data:`sonar` 通过超声波反射来判断前方障碍物的距离，其 :data:`distance` 属性用来查询前方障碍物的距离（米）
- 红外传感器 :data:`ir_sensors` 自身能发出的红外光，并感应的红外反射的强弱。:data:`state` 属性是一个3元素组成的元组，分别表示3个传感器是否接收到红外反射，0 表示没有接收到反射，1 表示有较强的反射


查询传感器状态
----------------

以下程序每隔 0.3 秒查询一次传感器的状态。试试按动按钮，在小车前摆放障碍物，或者将小车拿起再放下，观察传感器状态的变化：

.. code:: python

    from rcute_cozmars import Robot
    import time

    with Robot('xxxx') as robot:
        while True:
            print('按钮状态：', '按下' if robot.touch_sensor.touched else '松开')
            print('红外传感器状态：', robot.ir_sensors.state)
            print('前方障碍物距离：', robot.sonar.distance, '米')
            print('............................')
            time.sleep(.3)

以下程序通过不断查询声纳的状态，当前方障碍物距离小于 5 cm 时发出报警：

.. code:: python

    from rcute_cozmars import Robot
    import time

    with Robot('xxxx') as robot:

        while True: # 不断循环，按 Ctrl + C 退出

            if robot.sonar.distance < 0.05:
                robot.speaker.beep([500, 500])

            time.sleep(.3)

回调函数
----------------

但上面的程序需要一遍遍地查询状态数据，显得很“费劲”

更好的办法是利用 :data:`sonar` 的 :data:`when_in_range` 属性设置一个回调函数，当前方有障碍物进入 :data:`distance_threshold` 范围内时，该函数就会被自动调用：

.. code:: python

    from rcute_cozmars import Robot
    from signal import pause

    with Robot('xxxx') as robot:

        def ring(dist):
            robot.speaker.beep([500, 500])

        robot.sonar.distance_threshold = 0.05
        robot.sonar.when_in_range = ring

        pause() # 让程序在此暂停，按 Ctrl + C 退出

.. note::

    回调函数是事先指定的对某事件进行相应的函数，当相关事件发生时该函数就会自动被调用


顾名思义，:data:`sonar.when_out_of_range` 是当前方有障碍物离开 :data:`distance_threshold` 范围时会被调用的函数

而通过 :data:`ir_sensors.when_state_changed` 属性可以设置当红外传感器状态变换时被调用的函数，可以用来做经（无）典（聊）的寻迹小车实验：

.. code:: python

    from rcute_cozmars import Robot
    from signal import pause

    with Robot('xxxx') as robot:

        def steer(state):
            robot.motor.speed = state[0], state[2]

        robot.ir_sensors.when_state_changed = steer

        pause()

.. note::

    底部的3个红外传感器 :data:`ir_sensors` 也可以像数组引索那样使用

    >>> robot.ir_sensors.state            # 取得三个3个红外传感器的状态
    >>> robot.ir_sensors[1].state         # 取得中间红外传感器的状态
    >>> robot.ir_sensors['middle'].state  # 同上

:data:`touch_sensor` 的回调函数就更丰富了，有 :data:`when_touched` 、:data:`when_released`、 :data:`when_long_touched` 和 :data:`when_double_touched` ，分别是当按钮被触摸、被释放、被长按、被双击时的回调函数，这里就不一一演示了，请试着阅读以下相关的 API，自己测试一下！

.. seealso::

    `rcute_cozmars.touch_sensor <../api/touch_sensor.html>`_ ， `rcute_cozmars.sonar <../api/sonar.html>`_  ， `rcute_cozmars.ir_sensors <../api/ir_sensors.html>`_

后面还会介绍另外两个传感器：摄像头和麦克风。别急，休息，休息一会儿 ...