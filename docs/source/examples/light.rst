要有光
========

Cozmars 总是充满好奇心，因此作者给它配备了两盏炫酷的七彩 LED 大灯，方便它在黑暗中探险。

这两盏灯就藏在声纳模块的内部，用 :data:`lights` 表示。默认是关闭的（亮度为 0 ），你可以通过 :data:`brightness` 和 :data:`color` 属性分别设置灯的亮度和颜色：

    >>> robot.lights.brightness = 0.5   # 设置亮度为 50%
    >>> robot.lights.color = 'red'      # 设置颜色为红色

也可以分别设置两灯的颜色和亮度：

    >>> robot.lights.brightness = (0.2, 0.6)
    >>> robot.lights.color = ('green', 'blue')

.. warning::

    亮度不要设置太高，以免伤眼！

你也可以单独控制一盏灯而不改变另一盏灯的状态，比如，通过 :data:`lights[0]` 或 :data:`lights['left']` 来控制左灯：

    >>> robot.lights[0].color = 'white'          # 单独控制左灯
    >>> robot.lights['left'].brightness = 0      # 关闭左灯

:data:`lights[1]` 或 :data:`lights['right']` 都可以表示右灯。

:meth:`set_brightness` 方法的可以通过设置 :data:`fade_speed` 或 :data:`fade_duration` 参数来指定亮度渐变的速度或时间。

下面的程序模拟警灯，设置灯为红蓝两色，交替闪烁：

.. code:: python

    from rcute_cozmars import Robot

    with Robot() as robot:

        robot.lights.color = 'red', 'blue'
        robot.lights.brightness = 1, 0
        for i in range(3):
            robot.lights.set_brightness((0,1), fade_duration=0.5)
            robot.lights.set_brightness((1,0), fade_duration=0.5)

        robot.lights.brightness = 0