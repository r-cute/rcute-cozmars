Cozmars' playmate-Rubik's Cube
=======================

Connect cube
----------

The Rubik's Cube is an accessory independent of the Cozmars robot. To control the Rubik's Cube or obtain sensor data from the Rubik's Cube, it is necessary to establish a connection with the Rubik's Cube. The method is very similar to :class:`Robot`.

After pressing the power switch, first import :class:`rcute_cozmars.Cube`

.. code:: python

    from cozmars import Cube

.. raw:: html

    <style> .red {color:#E74C3C;} </style>

.. role:: red

Then to establish a connection with the Rubik's Cube, you can use the :red:`with` syntax:

.. code:: python

    from rcute_cozmars import Cube
    import time

# Assuming that the serial number of the Rubik's Cube is 556a, you need to replace it with the serial number of your Rubik's Cube!
     with Cube('556a') as cube:
         cube.color ='red' # red light for 3 seconds
         time.sleep(3)


You can also explicitly call the :meth:`connect` and :meth:`disconnect` methods to establish and disconnect the connection:


    >>> from rcute_cozmars import Cube
    >>> cube = Cube('556a')
    >>> cube.connet()
    >>> cube.color ='red'
    >>> cube.disconnect() # Finally remember to disconnect


.. note::

    The Rubik's Cube can only be connected to one program

Several attributes
---------------

We can control the Rubik's Cube or query the status of the Rubik's Cube through a few simple attributes or methods:

-:data:`color` property can query or change the GBR color of the Rubik's cube LED
-The :data:`static` attribute is used to indicate whether the cube is still
-:data:`last_action` property can query the last action of the Rubik's Cube
-:data:`top_face` When the Rubik’s Cube is stationary, this attribute is used to query which side of the Rubik’s Cube is facing up. The return value is the color corresponding to the QR code on the upper side. When the Rubik’s Cube is not stationary, it returns `None`

..
    -The :data:`acc` attribute is used to query the acceleration/gravity vector of the Rubik’s cube


Gesture Recognition
-----------

The Rubik’s cube has a built-in motion sensor, supports rich gesture recognition, and corresponds to many different callback functions as follows:

-:data:`when_flipped` is called when the cube is flipped 90 degrees or 180 degrees (with angle parameter)
-:data:`when_pushed` is called when the cube is translated (with direction parameter, indicated by color)
-:data:`when_rotated` is called when the cube is rotated clockwise/counterclockwise (with direction parameter)
-:data:`when_shaked` is called when the cube is shaken
-:data:`when_tilted` is called when the cube is tilted (with direction parameter, indicated by color)
-:data:`when_tapped` is called when tapping the cube
-:data:`when_fall` is called when the cube is weightless/free fall
-:data:`when_moved` is called when the cube is moved (including the above actions)
-:data:`when_static` is called when the cube returns to static

The following program connects the Rubik's Cube and the Cozmars robot respectively. When the Rubik's Cube turns clockwise, the robot turns right, and when the Rubik's Cube rotates counterclockwise, the robot turns left:

.. code:: python

    from rcute_cozmars import Cube, Cozmars

    with Cube('556a') as cube, Cozmars('0a3c') as robot:

        def turn(direction):
            if direction =='CW': # rotate clockwise
                robot.turn_right(2)
            elif direction =='CCW': # rotate counterclockwise
                robot.turn_left(2)

        cube.when_rotated = turn
        input('Enter to end the program')

Let's look at another example, using tilted gesture:

.. code:: python

    from rcute_cozmars import Cube, Cozmars

    with Cube('556a') as cube, Cozmars('0a3c') as robot:

        # When the magic direction tilts on the different colored surfaces, the robot makes different actions
        def move_robot(dir):
            if dir =='red':
                robot.head.angle = 20
            elif dir =='green':
                robot.head.angle = -20
            elif dir =='blue':
                robot.lift.height = 1
            elif dir =='yellow':
                robot.lift.height = 0

        cube.when_tilted = move_robot
        input('Enter to end the program')

.. note::

    As you can see, the serial numbers of Rubik's Cube and Cozmars are not the same!
    The above procedures have established connections with Cozmars and Rubik’s Cube respectively


.. seealso::

    `rcute_cozmars.Cube <../api/cube.html>`_