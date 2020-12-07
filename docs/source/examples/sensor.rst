Sensor and callback function
=================

Robots need to be able to perceive their surroundings, and light can only move machines

This section first introduces three simple sensors on Cozmars: the top button: data:`button`, the front sonar: data:`sonar` (ultrasonic distance sensor), and the bottom two infrared sensors: data :`infrared`


Each of the three sensors has some attributes to query its status:

-Button :data:`button` has three attributes: :data:`pressed`, :data:`held`, :data:`double_pressed`, which respectively indicate whether the button is pressed, long pressed and double-clicked
-Sonar :data:`sonar` judges the distance of obstacles ahead by ultrasonic reflection, and its :data:`distance` attribute is used to query the distance of obstacles ahead (meters)
-Infrared sensor :data:`infrared` The infrared light it can emit and the intensity of infrared reflection it senses. The :data:`state` attribute is a two-element tuple, which respectively indicate whether the left and right sensors receive infrared reflections, 0 means no or very weak reflection, and 1 means strong reflection


.. note::

    Like the motor :data:`motor`, the two infrared sensors are logically regarded as a whole

Query sensor status
----------------

The following program queries the sensor status every 0.3 seconds. Try to press the button to place obstacles in front of the trolley, or pick up the trolley and then put it down, and observe the changes in the sensor status:

.. code:: python

    from rcute_cozmars import Robot
    import time

    with Robot('0a3c') as robot:
        while True:
            print('Button status:','Pressed' if robot.button.pressed else'Release')
            print('Infrared sensor state:', robot.infrared.state)
            print('Distance of obstacles ahead:', robot.sonar.distance,'meter')
            print('............................')
            time.sleep(.3)

The following program continuously inquires the status of the sonar, and an alarm is issued when the distance of the obstacle in front is less than 5 cm:

.. code:: python

    from rcute_cozmars import Robot
    import time

    with Robot('0a3c') as robot:

        while True: # Keep looping, press Ctrl + C to exit

            if robot.sonar.distance <0.05:
                robot.buzzer.set_tone('C4', 1)

            time.sleep(.3)

Callback
----------------

But the above program needs to query the status data over and over again, which seems very "struggling"

A better way is to use the :data:`when_in_range` property of :data:`sonar` to set a callback function. When an obstacle enters the range of :data:`threshold_distance`, the function will be called automatically:

.. code:: python

    from rcute_cozmars import Robot
    from signal import pause

    with Robot('0a3c') as robot:

        def ring(dist):
            robot.buzzer.set_tone('C4', 1)

        robot.sonar.threshold_distance = 0.05
        robot.sonar.when_in_range = ring

        pause() # Let the program pause here, press Ctrl + C to exit

.. note::

    The callback function is a function that is specified in advance to correspond to an event, and the function will be automatically called when the relevant event occurs


As the name implies, :data:`sonar.when_out_of_range` is a function that will be called when the front side has an obstacle to leave the :data:`threshold_distance` range

And through the :data:`infrared.when_state_changed` property, you can set the function to be called when the state of the infrared sensor changes, which can be used to do a classic tracing car experiment:

.. code:: python

    from rcute_cozmars import Robot
    from signal import pause

    with Robot('0a3c') as robot:

        def steer(state):
            robot.motor.speed = state

        robot.infrared.when_state_changed = steer

        pause()



The callback functions of :data:`button` are more abundant, including: data:`when_pressed`, :data:`when_released`, :data:`when_held` and :data:`when_double_pressed`, respectively, when the button is pressed The callback functions when released, long-pressed, and double-clicked are not demonstrated here. Please try to read the following related APIs and test it yourself!

.. seealso::

    `rcute_cozmars.button <../api/button.html>`_, `rcute_cozmars.sonar <../api/sonar.html>`_, `rcute_cozmars.infrared <../api/infrared.html>`_

Two other sensors will be introduced later: camera and microphone. Don't worry, rest, rest for a while...