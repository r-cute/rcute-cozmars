异步模式
================

我们前面一直在使用同步模式控制 Cozmars，其实还有两种异步的控制模式。这里只能做个非常简略的介绍

concurrent 异步模式
-------------------------------

如果要让机器人的头部和手臂在 2 秒内 *同时* 抬起，我们大概会这样做：

.. code:: python

    from rcute_cozmars import Robot

        with Robot('0a3c') as robot:
            robot.lift.set_height(1, duration=2)
            robot.head.set_angle(20, duration=2)

但实际效果是，机器人先举手，再抬头，一共用了 4 秒

试试把上面代码中的 :data:`Robot` 改成 :data:`AsyncRobot` ，对比一下效果：

.. code:: python

    from rcute_cozmars import AsyncRobot

        with AsyncRobot('0a3c') as robot:
            robot.lift.set_height(1, duration=2) # 不等指令执行完毕就立刻执行下一条指令
            robot.head.set_angle(20, duration=2)

            input()

看出来区别了吗？这回举手和抬头是 *同时* 动作的，一共只用 2 秒。

:data:`AsyncRobot` 的用法和 :data:`Robot` 一样，只是在向机器人发送指令时，不等指令执行结束就立刻返回，接着执行下一条指令。

实际上，以上两条指令都分别返回了一个 :data:`concurrent.futures.Future` 对象，如果要等待一条指令执行完毕再开始下一条指令，则要调用该对象的 :meth:`result` 方法

.. code:: python

    from rcute_cozmars import AsyncRobot

        with AsyncRobot('0a3c') as robot:
            robot.lift.set_height(1, duration=2).result() # 等待指令执行完毕再接着执行下一条指令
            robot.head.set_angle(20, duration=2).result() # 这样就和原来效果一样的，用时 4 秒

async 异步模式
---------------------

另一种异步模式是使用 *协程*，对应的类是 :data:`AioRobot`，这是 Cozmars 程序内部的运行方式，也是我们在 `自定义 animation <examples/animation.html#id1>`_ 时要使用协程的原因。

我们已经稍微见识过，这里就不再演示了。除了开发 animation，你应该不需要用到这个模式：）

.. warning::

    需要注意的是，不能 *同时* 有两条指令控制机器人的同一个元件！

    比如一条抬头的指令还未执行完，就立刻执行另一条低头的指令，这可能会损坏舵机


.. note::

    对应地，魔方也同样有三个类 :data:`Cube` , :data:`AsyncCube` 和 :data:`AioCube` 分别实现三种不同的控制方式

.. seealso::

    `concurrent.futures.Future <https://docs.python.org/zh-cn/3/library/concurrent.futures.html#future-objects>`_ ，
    `asyncio <https://docs.python.org/zh-cn/3/library/asyncio-task.html>`_