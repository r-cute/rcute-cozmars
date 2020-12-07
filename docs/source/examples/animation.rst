Animation
==============

An animation is a set of pre-defined actions, such as the built-in animation :data:`'pick_up_cube'`, which can be viewed through Cozmars' :data:`animation_list` property, and called by the :meth:`animate` method.

The first parameter of Cozmars' :meth:`animate` method is the name of the action, and other optional parameters can be accepted. For example, the action of picking up the cube :data:`'pick_up_cube'` has a :data:`show_view` parameter to specify whether to display the camera screen. Place the Rubik's Cube near Cozmars and try:

    >>> robot.animate('pick_up_cube', show_view=True)

The following content is a bit "super-class" for Python beginners, so take care of it...

Custom animation
---------------------

The fun part of Animation is that it can be customized, which is similar to defining a function in advance and calling it when needed. I say "similar" because what we want to define is not a function but a coroutine. It doesn't matter if you haven't heard of a "coroutine". It is very similar in form to a function. Do it first.

With the action of picking up the cube, let's try to customize an action of putting down the cube, just call it'put_down_cube':

.. code:: python

    from rcute_cozmars import Robot, animations

    # Define a coroutine at the beginning of async def
    async def put_down_cube(robot):
        await robot.lift.height(0) # Put down the arm
        await robot.backward(1) # Back 1 second

    # That's it, it's easy, one step less than the elephant in the refrigerator

    # Next, add our custom action to the action list
    animations.update({'put_down_cube', put_down_cube})

    # Then you can use this action
    with Robot('0a3c') as robot:
        robot.animate('pick_up_cube')
        robot.animate('put_down_cube')

.. note::

    The custom animation coroutine needs to accept robot as the first parameter, and can also have other optional parameters.

In this coroutine, the command of the called robot action must also be changed to the method of invoking the coroutine. For example, we change :data:`robot.backward(1)` to:data:`await robot.backward(1 )`, change:data:`robot.lift.height = 0` to:data:`await robot.lift.height(0)`

Face change animation
------------------
Let's try to transform the `Sichuan Opera Change Face <move.html#id5>`_ program written earlier into a custom action'bian_lian', pay attention to the difference between the comparison function and the coroutine:

.. code:: python

    import asyncio

    async def bian_lian(robot):
        robot.head.default_speed = None
        robot.lift.default_speed *= 2

        for color in ['white','red','yellow','lightgreen']:
            await robot.head.angle(-15)
            await robot.lift.height(1)
            await robot.eyes.color(color)
            await robot.head.angle(0)
            await robot.lift.height(0)
            await asyncio.sleep(3)

    from rcute_cozmars import animations
    animations.update({'bian_lian', bian_lian})

`It’s not as good as the others <https://www.zhihu.com/question/22524653/answer/574482596>`_
-------------------------------------------------- -----------------------------------------------

Now you can save this code in a file called :data:`bian_lian_animation.py`, and then share it with others. After someone quotes your file, you can use this action in his/her code:

.. code:: python

    import bian_lian_animation
    from rcute_cozmars import Robot

    with Robot('03e5') as robot:
        robot.animate('bian_lian')