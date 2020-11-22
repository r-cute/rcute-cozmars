显示屏：并非木得感情的证明
===========================

眼睛是心灵的窗户。Cozmars 用它的卡姿兰大眼睛把心情都写在了 240x135 像素的显示屏上，证明自己绝非木得感情

眼睛和表情
-------------

眼睛 :data:`eyes` 可以通过设置 :data:`color` 和 :data:`expression` 来设置眼睛的颜色和表情。可以通过 :data:`eyes` 的 :data:`expression_list` 得到支持的所有表情

让机器人表演一次川剧变脸：

.. code:: python

    from rcute_cozmars import Robot
    from time import sleep

    with Robot('0a3c') as robot:

        robot.eyes.color = 'red'
        robot.eyes.expression = 'angry'
        sleep(3)

        robot.lift.height = 1
        robot.eyes.color = 'cyan'
        robot.eyes.expression = 'happy'
        robot.lift.height = 0
        sleep(5)

如果要隐藏眼睛，只需调用 :data:`eyes` 的 :meth:`hide` 方法； 而 :meth:`show` 方法让眼睛重新出现

.. note ::

    设置颜色时可以用表示颜色的字符串，例如 `robot.eyes.color = 'yellow'`，也可以用 BGR 色彩模式 `robot.eyes.color = (255, 255, 0)`

    注意：为了与 opencv 一致，我们使用 BGR 而不是 RGB 色彩模式！

图像和文字
------------

:class:`Robot` 还有一个 :data:`screen` 属性用来直接控制显示屏，用它的 :meth:`display` 方法来显示图片

:data:`screen` 的 :data:`brightness` 属性可以用来设置显示屏的亮度，`1` 表示最亮，`0` 表示全暗，默认是 `0.05` ；也可以通过 :meth:`set_brightness` 方法的 :data:`fade_duration` 或 :data:`fade_speed` 参数来控制亮度的渐变速度

以下的程序显示一个心跳在屏幕上：

.. code:: python

    from rcute_cozmars import Robot
    import cv2

    with Robot('0a3c') as robot:

        # 读取一幅 ❤❤ 图片
        heart = cv2.imread('./heart.png')

        # 在显示屏显示图片
        robot.screen.display(heart)

        # 然后让显示屏的亮度不断变化
        for _ in range(3):
            robot.screen.set_brightness(0, fade_duration=0.5)
            robot.screen.set_brightness(1, fade_duration=0.5)

        # 如果要让眼睛重新出现:
        # robot.eyes.show()

以下图片是程序中用到的 heart.png ，你可以右键把它另存到本地

.. image:: ./heart.png

另外，还可以用 :data:`screen` 的 :meth:`text` 方法显示简单的文本，比如：

.. code:: python

    from rcute_cozmars import Robot
    from time import sleep

    with Robot('0a3c') as robot:
        robot.screen.text('I am...')
        sleep(2)
        robot.screen.text('COZMARS!', color='white')
        sleep(2)

.. seealso::

    `rcute_cozmars.screen <../api/screen.html>`_ ， `rcute_cozmars.animation.EyeAnimation <../api/animation.html#rcute_cozmars.animation.EyeAnimation>`_