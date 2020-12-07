Move
===============

The movable parts of the Cozmars robot are the head, arms and wheels. In this lesson, we use command line interaction to make the robot move.

First connect the robot:

    >>> from rute_cozmars import Robot
    >>> robot = Robot('0a3c')
    >>> robot.connect()

Raise hand
-------------

We use the robot's :data:`lift` property to control the robot's arm, and set the :data:`height` property of :data:`lift` to control the height of the arm lift:

    >>> robot.lift.height = 1
    >>> robot.lift.height = 0

The height of the arm can be set to a number between 0 and 1. Enter the above two commands, you can see that the robot arm is raised and then lowered.

The moving speed of the arm can be set by :data:`default_speed`, the default is 2/sec. Let's reduce the speed to 0.5 and try "a slow motion with left hand and right hand":

    >>> robot.lift.default_speed = 0.5
    >>> robot.lift.height = 1
    >>> robot.lift.height = 0

The setting of :data:`default_speed` is effective for subsequent arm movements. If you want to temporarily change the moving speed of the arm, you can use the :meth:`set_height` method to control. The following two sentences of code are equivalent to the above code:

    >>> robot.lift.set_height(1, speed=0.5)
    >>> robot.lift.set_height(0, speed=0.5)

If you feel that the speed is not intuitive enough, :meth:`set_height` can also set the arm movement time through the :data:`duration` parameter, for example, to raise the arm within two seconds:

    >>> robot.lift.set_height(1, duration=2)

Nod
-------------

The head of the robot is controlled by the :data:`head` property. You can set the :data:`angle` property of :data:`head` to control the angle of head rotation. The head can be rotated between -20 and 20 degrees, 0 degrees means looking straight ahead, and a negative number means lowering your head. For example, let the robot nod twice:

     >>> for i in range(2):
     ... robot.head.angle = -20
     ... robot.head.angle = 0

The head control is very similar to the arm control. :data:`head` also has :data:`default_speed` property (default is 60 degrees/sec) and :meth:`set_angle` method. I won’t be too wordy here, you can Explore by yourself

move forward
--------------

Let's operate the robot's motor :data:`motor` to control the movement of the robot

.. note::

    In fact, there is a motor on the left and right of the robot. From a grammatical point of view, the plural "motors" should be used, but let's logically regard them as a whole for the time being, because we also set the motor speed in a whole way :)


.. warning::

    Please be careful not to let the robot fall off the table when moving!


The speed of the motor :data:`speed` can be a number between -1~1, 0 means stop, 1 means full speed forward, and of course a negative number means backward:

    >>> robot.motor.speed = 1
    >>> robot.motor.speed = -1
    >>> robot.motor.speed = 0

The speed of the motor can also be a tuple (`tuple`) composed of two elements, which respectively represent the speed of the left and right motors. For example, by making the two motors turn in opposite directions, the robot can make a circle on the spot:

    >>> robot.motor.speed = (1, -1)
    >>> robot.motor.stop() # The effect is equivalent to robot.motor.speed=0

:data:`motor` also has a :meth:`set_speed` method to set speed and duration. For example, to rotate the robot for 5 seconds:

    >>> robot.motor.set_speed((1, -1), duration=15)





Finally, don't forget to disconnect the program from the robot:

    >>> robot.disconnect()

Sichuan Opera Changing Face
-------------------

The following is a complete code to make the robot perform a face-changing magic:

.. code:: python

    import time
    from rcute_cozmars import Robot

    with Robot('0a3c') as robot:

        robot.head.default_speed = None # defaul_speed is set to None, which means the fastest speed
        robot.lift.default_speed *= 2

        for color in ['white','red','yellow','lightgreen']:
            robot.head.angle = -15
            robot.lift.height = 1
            robot.eyes.color = color
            robot.head.angle = 0
            robot.lift.height = 0
            time.sleep(3)


.. seealso::

    `rcute_cozmars.lift <../api/lift.html>`_, `rcute_cozmars.head <../api/head.html>`_, `rcute_cozmars.motor <../api/motor.html>`_


    `rcute_cozmars.Robot.forward <../api/robot.html#rcute_cozmars.robot.Robot.forward>`_, `rcute_cozmars.Robot.backward <../api/robot.html#rcute_cozmars.robot.Robot.backward >`_, `rcute_cozmars.Robot.turn_left <../api/robot.html#rcute_cozmars.robot.Robot.turn_left>`_, `rcute_cozmars.Robot.turn_right <../api/robot.html#rcute_cozmars.robot .Robot.turn_right>`_