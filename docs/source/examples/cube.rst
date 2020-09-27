魔方
==============

连接魔方
----------

魔方 Cube 是独立于 Cozmars 机器人的，要控制魔方或者获取魔方的传感器数据，需要与魔方建立连接。方法和 :class:`Robot <./examples/connect.html>`_ 十分类似。

按下电源开关后，首先导入 :class:`rcute_cozmars.Cube`:

..code:: python

    from cozmars import Cube

.. raw:: html

    <style> .red {color:#E74C3C;} </style>

.. role:: red

然后与魔方建立连接，可以使用 :red:`with` 语法：

    .. code:: python

        from rcute_cozmars import Cube
        import time

        with Cube('192.168.1.103') as cube:
            cube.color = (255, 0, 0) # 亮红灯3秒钟
            time.sleep(3)

也可以显示地调用 :meth:`connect` 和 :meth:`disconnect` 方法来建立和断开连接：


    >>> from rcute_cozmars import Cube
    >>> cube = Cube('192.168.1.103')
    >>> cube.connet()
    >>> cube.color = (255, 0, 0)
    >>> cube.disconnect()  # 最后记得断开连接

.. note::

    魔方也是同时只能与一个程序连接

几个属性
---------------

我们可以通过几个简单的属性或方法来控制魔方或查询魔方的状态：

- :data:`color` 属性能查询或改变魔方 LED 的 RGB 颜色
- :data:`static` 属性用来指示魔方是否在静止
- :data:`last_action` 属性可以查询魔方的上一个动作
- :data:`acceleration` 属性用来查询魔方的加速度/重力的矢量，可以此推断魔方哪个面朝上

回调函数
-----------

魔方有以下几个回调函数，当特定动作发生时会被调用（这些动作的灵感来源于小米魔方控制器）：

- :data:`when_flipped_90` 在魔方被翻转90度时调用
- :data:`when_flipped_180` 在魔方被翻转180度时调用
- :data:`when_moved` 在魔方被水平推动时调用
- :data:`when_rotated_clockwise` 在魔方被顺时针旋转时调用
- :data:`when_rotated_counter_clockwise` 在魔方被逆时针旋转时调用
- :data:`when_shaked` 在魔方被摇晃时调用

下面的程序分别连接魔方和 Cozmars 机器人，当魔方顺时针转动时让机器人右转，当魔方逆时针转动时让机器人左转：

..code:: python

    from rcute_cozmars import Cube, Cozmars

    with Cube('192.168.1.103') as cube, Cozmars('192.168.1.102') as robot:
        cube.when_rotated_counter_clockwise = lambda: robot.turn_left(3)
        cube.when_rotated_clockwise = lambda: robot.turn_right(3)
        input('回车结束程序')

关机
-----------
魔方的关机就比较随意了，直接按下电源开关让它弹起就是了


.. seealso::

    `rcute_cozmars.Cube <../api/cube.html>`_