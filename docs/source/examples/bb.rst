能动手也要 bb
=================

:class:`Robot` 的 :data:`buzzer` 属性代表机器人内部的一个蜂鸣器，蜂鸣器能以不同的频率振动，从而发出不同的 `音调`。

.. |Tone| raw:: html

    <a href='https://gpiozero.readthedocs.io/en/stable/api_tones.html' target='blank'>gpiozero.tones.Tone</a>

.. note::

    这里所说的 `音调` ，在程序中可以用不同的数据类型表示。

    比如 C 大调 do re me fa so la si 中的 do 音，音乐记号是 `'C4'` ，频率是 261.63 Hz，MIDI 代码是 #60，那么，`'C4'` 、 `261.63` 和 `60` 都可以用来表示这个音调，也可以用 |Tone| 对象来表示

    用 `None` 或 `0` 表示静音

只要改变 :data:`buzzer` 的 :data:`tone` 属性就能改变蜂鸣器的音调：

    >>> from gpiozero.tones import Tone
    >>> # 以下四句代码效果是相同的，所以你不会听到音调的变化。尝试改变频率或音乐记号再听听：
    >>> robot.buzzer.tone = 261.63
    >>> robot.buzzer.tone = 'C4'
    >>> robot.buzzer.tone = 60
    >>> robot.buzzer.tone = Tone('C4')
    >>> # 静音：
    >>> robot.buzzer.quiet()  # 或者:
    >>> robot.buzzer.tone = 0

播放单个 `音调` 比较方便的办法是用 :data:`buzzer` 的 :meth:`set_tone` 方法同时设置 `音调` 和播放时长：

    >>> robot.buzzer.set_tone('A4', duration=2)

哼两句
---------------

to be continuned ...

可以用 :data:`buzzer` 的 :meth:`play` 方法来连续播放一段音乐。运行下面一段程序，猜猜是周杰伦《晴天》的中的哪一句

.. code:: python

    from rute_cozmars import Robot
    import time

    with Robot('192.168.1.102') as robot:
        with robot.buzzer:

            for s in song:
                robot.buzzer.input_stream.put(s)
                time.sleep(.5)
                robot.buzzer.input_stream.put(None)
                time.sleep(.1)

