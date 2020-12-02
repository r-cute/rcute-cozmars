动起来
===============

Cozmars 机器人身上能动的部件是头部、手臂和轮子。这一节课我们用命令行交互的方式来让机器人做做运动。

首先连接机器人：

    >>> from rute_cozmars import Robot
    >>> robot = Robot('0a3c')
    >>> robot.connect()

举举手
-------------

我们通过机器人的 :data:`lift` 属性来控制机器人的手臂，通过设置 :data:`lift` 的 :data:`height` 属性可以控制手臂举起的高度：

    >>> robot.lift.height = 1
    >>> robot.lift.height = 0

手臂的高度可以设置为 0 和 1 之间的数，输入以上两句命令，可以看到机器人的手臂举起后再放下。

手臂的移动速度可以通过 :data:`default_speed` 来设置，默认是 2/秒。我们把速度降到 0.5 ，来试试“左手右手一个慢动作”：

    >>> robot.lift.default_speed = 0.5
    >>> robot.lift.height = 1
    >>> robot.lift.height = 0

:data:`default_speed` 的设置对后续的手臂移动都有效。如果要临时改变手臂的移动速度，可以用 :meth:`set_height` 方法来控制，以下两句代码和上面的代码是等效的：

    >>> robot.lift.set_height(1, speed=0.5)
    >>> robot.lift.set_height(0, speed=0.5)

如果觉得速度不够直观， :meth:`set_height` 也可以通过 :data:`duration` 参数设置手臂移动的时间，比如要让手臂在两秒之内抬起：

    >>> robot.lift.set_height(1, duration=2)

点点头
-------------

机器人的头部通过 :data:`head` 属性来控制，可以设置 :data:`head` 的 :data:`angle` 属性来控制头部转动的角度。头部可以在 -30~30 度之间转动，0 度表示平视前方，负数则表示低头。比如，让机器人点两下头：

    >>> for i in range(2):
    ...     robot.head.angle = -30
    ...     robot.head.angle = 0

头部的控制和手臂的控制非常相似， :data:`head` 也有 :data:`default_speed` 属性（默认是 60 度/秒）和 :meth:`set_angle` 方法，这里就不啰嗦了，你可以自己探索

向前进
--------------

下面我们来操作机器人的马达 :data:`motor` ，从而控制机器人的移动

.. note::

    实际上机器人左右各有一个马达，从语法的角度讲应该用复数“motors”，但我们暂且在逻辑上把它们看成一个整体吧，因为我们也是以整体的方式来设置马达速度的 :)


.. warning::

    移动的时候请小心别让机器人从桌上掉下来！


马达的速度 :data:`speed` 可以是 -1~1 之间数，0 表示停止，1 是全速前进，那负数当然就是后退喽：

    >>> robot.motor.speed = 1
    >>> robot.motor.speed = -1
    >>> robot.motor.speed = 0

马达的速度也可以是由两元素组成的元组( `tuple` )，两个元素分别表示左右马达的速度。比如，通过让两个马达转向相反，可以让机器人原地转圈：

    >>> robot.motor.speed = (1, -1)
    >>> robot.motor.stop()  # 效果等同于 robot.motor.speed=0

:data:`motor` 还有一个 :meth:`set_speed` 方法，用来设置速度和持续时间。比如，要机器人转圈 5 秒：

    >>> robot.motor.set_speed((1, -1), duration=15)





最后，不要忘记断开程序与机器人的连接：

    >>> robot.disconnect()

伸展运动
-------------------

下面是一段完整的代码，让机器人做个伸展运动：

.. code:: python

    from rcute_cozmars import Robot

    with Robot('0a3c') as robot:

        robot.head.default_speed = None # defaul_speed 设为 None，表示最快速度

        robot.motor.speed = 0.5
        robot.head.angle = 30
        robot.lift.set_height(1, duration=2)

        robot.motor.speed = -0.5
        robot.head.angle = -30
        robot.lift.set_height(0, duration=2)

        robot.motor.stop()
        robot.head.set_angle(0, duration=1)


.. seealso::

    `rcute_cozmars.lift <../api/lift.html>`_ ，`rcute_cozmars.head <../api/head.html>`_ ，`rcute_cozmars.motor <../api/motor.html>`_


    `rcute_cozmars.Robot.forward <../api/robot.html#rcute_cozmars.robot.Robot.forward>`_ ，`rcute_cozmars.Robot.backward <../api/robot.html#rcute_cozmars.robot.Robot.backward>`_ ， `rcute_cozmars.Robot.turn_left <../api/robot.html#rcute_cozmars.robot.Robot.turn_left>`_ ， `rcute_cozmars.Robot.turn_right <../api/robot.html#rcute_cozmars.robot.Robot.turn_right>`_