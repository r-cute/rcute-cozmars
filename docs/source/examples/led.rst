要有光
=============

为了方便 Cozmars 在夜晚探险，V2 版在显示屏旁边增加了一个 LED 灯，用 :data:`led` 属性表示。

它用法和 `控制显示屏的背光亮度 <screen.html#id3>`_ 一样，:data:`brightness` 属性用来调节亮度，:data:`default_fade_speed` 属性 和 :meth:`set_brightness` 方法用来控制渐变速度。

    >>> robot.led.brightness = 0.5 # 打开 LED（亮度 50%），请勿直视强光！
    >>> robot.led.brightness = 0   # 关闭 LED


.. seealso::

    `rcute_cozmars.led <../api/led.html>`_