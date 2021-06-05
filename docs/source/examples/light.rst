要有光
========

Cozmars 对世界充满了好奇，因此作者给它配备了两盏炫酷的七彩 LED 大灯，方便它在黑暗中探险。

这两盏灯就藏在声纳模块的内部，用 :data:`lights` 表示。默认是关闭的（亮度为 0 ），你可以通过 :data:`brightness` 和 :data:`color` 属性分别设置灯的亮度和颜色：

    >>> robot.lights.brightness = 0.5   # 设置亮度为 50%
    >>> robot.lights.color = 'red'      # 设置颜色为红色

也可以分别设置两灯的颜色和亮度：

    >>> robot.lights.brightness = (0.1, 0.5)
    >>> robot.lights.color = ('green', 'blue')

.. warning::

    建议亮度不要设置太高，以免伤眼！

通过使用引索，你也可以单独控制一盏灯而不改变另一盏灯的状态。引索的使用和前面介绍过的 :data:`motors` 一样：

    >>> robot.lights[0].color = 'yellow'
    >>> robot.lights[1].color = 'orange'
    >>> robot.lights['left'].brightness = 0
    >>> robot.lights['right'].set_brightness(0, fade_duration=2)

:meth:`set_brightness` 方法的可以通过设置 :data:`fade_speed` 或 :data:`fade_duration` 参数来指定亮度渐变的速度或时间。

下面的程序模拟警灯，设置灯为红蓝两色，交替闪烁：

.. code:: python

    from rcute_cozmars import Robot

    with Robot() as robot:

        robot.lights.color = 'red', 'blue'
        robot.lights.brightness = 1, 0
        for i in range(3):
            robot.lights.set_brightness((0,1), fade_duration=1)
            robot.lights.set_brightness((1,0), fade_duration=1)

        robot.lights.brightness = 0