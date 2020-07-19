心灵之窗——显示屏
=====================

眼睛是心灵的窗户。Cozmars 大眼睛眨呀眨，把它的心情都写在 240x135 像素的显示屏上

眼睛和表情
-------------

:class:`Robot` 的 :data:`eyes` 属性可以控制眼睛的颜色和表情。可以通过 :data:`eyes` 的 :data:`expression_list` 得到支持的所有表情

让机器人的表情从生气的红色变成开心的绿色：

.. code:: python

    from rcute_cozmars import Robot
    from time import sleep
    from signal import pause

    with Robot('192.168.1.102') as robot:

        time.sleep(3)
        robot.eyes.expression = 'angry'
        robot.eyes.color = (0, 0, 255)

        time.sleep(3)
        robot.eyes.expression = 'happy'
        robot.eyes.color = (255, 0, 0)

        pause()

如果要隐藏眼睛，只需调用 :data:`eyes` 的 :meth:`hide` 方法； 而 :meth:`show` 方法让眼睛重新出现

显示屏
---------

:class:`Robot` 还有一个 :data:`screen` 属性用来直接控制显示屏

:data:`screen` 的 :data:`brightness` 属性可以用来设置显示屏的亮度，`1` 表示最亮，`0` 表示全暗，默认是 `0.1` ；也可以通过 :meth:`set_brightness` 方法的 :data:`fade_duration` 或 :data:`fade_speed` 参数来控制亮度的渐变速度

以下的程序显示一个心跳在屏幕上：

.. code:: python

    from rcute_cozmars import Robot
    import cv2

    with Robot('192.168.1.102') as robot:

        # 先让眼睛隐藏起来
        robot.eyes.hide()

        # 在显示屏上展示一幅 ❤ 的图片
        heart = cv2.imread('./heart.jpg')
        robot.screen.display(heart)

        # 然后让显示屏的亮度不断变化
        for _ in range(5):
            robot.screen.set_brightness(0, fade_duration=0.5)
            robot.screen.set_brightness(1, fade_duration=0.5)

        # 如果要让眼睛重新出现:
        # robot.eyes.show()

以下图片是程序用到的 heart.jpg ，你可以右键把它另存到本地

.. image:: ./h.gif

.. seealso::

    `rcute_cozmars.screen <../api/screen.html>`_ ， `rcute_cozmars.animation.EyeAnimation <../api/animation.html#rcute_cozmars.animation.EyeAnimation>`_