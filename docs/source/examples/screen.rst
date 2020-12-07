Display screen: not proof of wooden feeling
===========================

The eyes are the windows of the soul. Cozmars wrote his mood on the 240x135-pixel display with its big eyes, proving that he is definitely not emotional

Eyes and expressions
-------------

Eyes :data:`eyes` You can set the color and expression of the eyes by setting :data:`color` and :data:`expression`. All emojis that can be supported by :data:`eyes` of :data:`expression_list`

    >>> robot.eyes.color ='red'
    >>> robot.eyes.expression ='angry'
    >>> robot.eyes.expression = ('happy','lightgreen') # Or, you can set the expression and color at the same time

If you want to hide the eyes, just call the :meth:`hide` method of :data:`eyes`; and the :meth:`show` method makes the eyes reappear. The dynamic effects of the eyes will take up a bit of Cozmars bandwidth. When you want to avoid network delays as much as possible, use the :meth:`stop` and :meth:`resume` methods to pause and continue the dynamic effects of the eyes.

.. note ::

    When setting the color, you can use a string representing the color, for example, `robot.eyes.color ='yellow'`, or use the BGR color mode `robot.eyes.color = (255, 255, 0)`

    Note: To be consistent with opencv, we use BGR instead of RGB color mode!

Display Image
------------

:class:`Robot` also has a :data:`screen` attribute to directly control the display screen, use its :meth:`display` method to display pictures

The :data:`brightness` property of :data:`screen` can be used to set the brightness of the display, `1` means the brightest, and `0` means all dark. In order to save power and protect the eyes, the default display brightness is `0.05 `;You can also use the :data:`fade_duration` or :data:`fade_speed` parameter of the :meth:`set_brightness` method to control the brightness gradient speed

The following program displays a heartbeat on the screen:

.. code:: python

    from rcute_cozmars import Robot
    import cv2

    with Robot('0a3c') as robot:

        # Read a picture ❤❤
        heart = cv2.imread('./heart.png')

        # Show pictures on the display
        robot.screen.display(heart)

        # Then let the brightness of the display keep changing
        for _ in range(3):
            robot.screen.set_brightness(0, fade_duration=0.5)
            robot.screen.set_brightness(1, fade_duration=0.5)

        # If you want to make the eyes reappear:
        # robot.eyes.show()

The following picture is the heart.png used in the program, you can right-click to save it locally

.. image:: ./heart.png

Display text
---------------

In addition, you can also use the :meth:`text` method of :data:`screen` to display simple text, such as:
=======

.. code:: python

    from rcute_cozmars import Robot
    from time import sleep

    with Robot('0a3c') as robot:
        robot.screen.text('I am...')
        sleep(2)
        robot.screen.text('COZMARS!', size=35, color='black', bg_color='cyan')
        sleep(2)

.. seealso::

    `rcute_cozmars.screen <../api/screen.html>`_, `rcute_cozmars.animation.EyeAnimation <../api/animation.html#rcute_cozmars.animation.EyeAnimation>`_