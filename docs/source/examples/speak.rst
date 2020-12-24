能动手也要 bb
===============

Cozmars V2 版相较于 V1 版的改进，是用扬声器取代了蜂鸣器。扬声器的频率响应更好，由音频功放驱动，能够播放数字音乐

好好说话
---------

扬声器用 :data:`speaker` 属性表示。有了它，Cozmars 就能说人话了

    >>> robot.speaker.say('不要睡，起来嗨')

在调用 :meth:`say` 函数时，可以指定 :data:`voice`、:data:`pitch`、:data:`volume`、:data:`speed` 参数来改变语言、音调、音量和语速

.. note::

    程序出错？如果你使用的是 Cozmars V1 版，请跳转 `这里 <../../v1/examples/bb.html>`_

到点了，网抑云
--------------

:data:`speaker` 的 :meth:`play` 函数能很方便地播放多种声音格式，只要把声音的文件路径、网址或 wav 数据作为 :meth:`play` 的参数即可

    >>> robot.speaker.play('goodbye yellow brick road.mp3')

各种歌曲顺手拈来，缓则“乐以教和”，躁可“动次打次”，取决于你喜欢怎样的 Cozmars

哼两句
--------

:meth:`beep` 函数通过播放不同频率的正弦波形，使扬声器可以模仿蜂鸣器，发出不同的 *音调*

.. |Tone| raw:: html

    <a href='https://gpiozero.readthedocs.io/en/stable/api_tones.html' target='blank'>gpiozero.tones.Tone</a>

.. note::

    这里所说的 *音调* ，在程序中可以用多种的数据类型表示。

    比如 C 大调 do re me fa so la si 中的 do 音，音乐记号是 `C4` ，频率是 261.63 Hz，MIDI 代码是 #60，那么，在代码中，`'C4'` 、 `261.63` 和 `60` 都可以用来表示这个音调，也可以用 |Tone| 对象来表示

    用 `None` 或 `0` 表示静音（休止符）

:meth:`beep` 的参数是 *音调* 构成的数组，默认每个 *音调* 为一拍，而被括号包围起来的 *音调* 每个为半拍，被两层括号包围起来的 *音调* 每个为 1/4 拍... 以此类推，每多一层括号拍数减半； 用 :data:`tempo` 参数来指定播放的速度（BPM），:data:`repeat` 来指定重复次数

运行下面一段程序，猜猜是周杰伦的哪首歌：

.. code:: python

    from rute_cozmars import Robot

    tones = ['D4', 'G4', 'G4', 'B4', 'C5', 'B4', 'A4',
            ('G4', 'A4'), 'B4', 'B4', 'B4', 'B4', ('A4', 'B4'), 'A4', 'G4']

    with Robot('0a3c') as robot:
        robot.speaker.beep(tones, tempo=120, repeat=2)


.. seealso::

    `rcute_cozmars.speaker <../api/speaker.html>`_