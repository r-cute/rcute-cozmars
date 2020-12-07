connection
==============

`rcute_cozmars` is a Python module used to control Cozmars robots and Cube cubes. To use this module, just import it at the beginning of the program:

.. code:: python

    import rcute_cozmars

But, usually we only need to import :class:`rcute_cozmars.Robot`:

.. code:: python

    from rcute_cozmars import Robot

Then create a new :class:`Robot` object with the robot's serial number or IP address as a parameter, and connect to the robot.

There are two connection methods:

.. raw:: html

    <style> .red {color:#E74C3C;} </style>

.. role:: red

.. raw:: html

    <style> .shell {color:#c65d09;font-weight:bold;font-size:14px} </style>

.. role:: shell

1. Use :red:`with` syntax, similar to file operations, it will automatically establish a connection with the robot, and automatically disconnect when the indented code block below :red:`with` ends:

    .. code:: python

        from rcute_cozmars import Robot
        # From now on assume that the serial number of the robot is '0a3c', you need to replace it with the serial number of your Cozmars!
        with Robot('0a3c') as robot:
            robot.forward(2) # Let the robot move forward for 2 seconds


2. Explicitly call the :meth:`connect` and :meth:`disconnect` methods to establish and disconnect the connection. This method is suitable for interactively controlling the robot in the terminal window:

    >>> from rcute_cozmars import Robot
    >>> robot = Robot('0a3c')
    >>> robot.connet()
    >>> robot.forward(2)
    >>> robot.disconnect() # Finally remember to disconnect

.. note::

    Did you notice the :shell:`>>>` symbol at the beginning of the above code? It means that these codes are commands entered in the terminal window;

    And the code block with *no* :shell:`>>>` symbol represents the entire code in the file

.. note::

    A Cozmars robot can only be connected to one program at the same time, and only after disconnecting can it accept the connection of the next program


.. seealso::

    `rcute_cozmars.Robot.connect <../api/robot.html#rcute_cozmars.robot.Robot.connect>`_, `rcute_cozmars.Robot.disconnect <../api/robot.html#rcute_cozmars.robot.Robot.disconnect >`_