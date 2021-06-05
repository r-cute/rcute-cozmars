能动手也要 bb
===============

    >>> robot.speaker.beep([500, 500]) # 让机器人发出两个 500Hz 的音节

:data:`speaker` 表示机器人内置的一个扬声器。有了它，Cozmars 就可以说话、播放数字音乐了。还是让我们从最简单的音调说起吧

哼小曲
--------

扬声器用 :data:`speaker` 属性表示。它的 :meth:`beep` 函数通过播放不同频率的正弦波形，使扬声器可以模仿蜂鸣器，发出不同的 `音调 <http://www.vibrationdata.com/tutorials2/piano.pdf>`_

.. note::

    这里所说的 *音调* ，在程序中可以用不同的数据类型表示。

    比如 C 大调 “do re me fa so la si” 中的 “la” 音，音乐记号是 A4，频率是 440 Hz，MIDI 代码是 69，那么 `'A4'` 、 `440.0` 和 `69` 都可以用来表示这个 *音调*

    用 `None` 或 `0` 表示静音（休止符）

:meth:`beep` 的参数是 *音调* 构成的数组，默认每个 *音调* 为一拍，而被括号包围起来的 *音调* 每个为半拍，被两层括号包围起来的 *音调* 每个为 1/4 拍... 以此类推，每多一层括号拍数减半； 用 :data:`tempo` 参数来指定播放的速度（BPM），:data:`repeat` 来指定重复次数

运行下面一段程序，猜猜是周杰伦的哪首歌：

.. code:: python

    from rute_cozmars import Robot

    tones = ['D4', 'G4', 'G4', 'B4', 'C5', 'B4', 'A4',
            ('G4', 'A4'), 'B4', 'B4', 'B4', 'B4', ('A4', 'B4'), 'A4', 'G4', 0]

    with Robot('xxxx') as robot:
        robot.speaker.beep(tones, tempo=120, repeat=2)

Rock n roll
---------------

:data:`speaker` 的 :meth:`play` 函数能很方便地播放多种声音格式，只要把声音的文件路径、网址或 wav 数据作为 :meth:`play` 的参数即可

    >>> robot.speaker.play('./waiting_for_the_end.mp3')

各类歌曲顺手拈来，缓则“乐以教和”，躁可“动次打次”，取决于你喜欢怎样的 Cozmars

好好说话
---------

要让 Cozmars 说人话，先要安装 `rcute-ai <https://rcute-ai.readthedocs.io/>`_

:class:`Robot` 的 :meth:`say` 函数能把 rcute-ai 的合成语音通过扬声器播放出来：

    >>> robot.say('不要睡，起来嗨')

:meth:`say` 函数还可以指定 :data:`voice`、:data:`pitch`、:data:`volume`、:data:`speed` 参数来改变语言、音调、音量和语速

.. seealso::

    `rcute_cozmars.speaker <../api/speaker.html>`_ ，`rcute_cozmars.Robot.say <../api/robot.html#rcute_cozmars.robot.Robot.say>`_ ，

