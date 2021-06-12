Animation
==============

一个 Animation 就是一组事先定义好的动作，例如自带的 animation :data:`'pick up cube'` ，可以通过 Cozmars 的 :data:`animation_list` 属性查看，通过 :meth:`animate` 方法调用。

Cozmars 的 :meth:`animate` 方法的第一参数是动作的名称，还可以接受其他的可选参数。比如拾取魔方的动作 :data:`'pick up cube'` ，就带有一个 :data:`show_camera_view` 参数用来指定是否显示摄像头画面。把魔方摆放在 Cozmars 附近，然后试试：

    >>> robot.animate('pick up cube', show_camera_view=True)

接下来的内容对 Python 初学者来说有点“超纲”，抓稳扶好了哦。。。

自定义 animation
---------------------

Animation 好玩的地方在于它是可以自定义的，类似于事先定义好一个函数，在需要的时候调用它就行。我说“类似”，是因为我们要定义的不是函数而是协程（coroutine），如果你没听过“协程”也没关系，它在形式上跟函数很像。先做再说。

有了拾取魔方的动作，我们也来试着自定义一个放下魔方的动作，就把它叫做 'put down cube' 吧：

.. code:: python

    from rcute_cozmars import Robot, animations

    # 用 async def 开头定义一个协程
    async def put_down_cube(robot):
        await robot.lift.height(0)  # 放下手臂
        await robot.backward(1)    # 后退 1 秒

    # 这就完了，简单吧，比大象关进冰箱还少一步

    # 接下来把我们自定义的动作加入动作列表里
    animations.update({'put down cube', put_down_cube})

    # 然后就可以使用这个动作了
    with Robot('xxxx') as robot:
        robot.animate('pick up cube')
        robot.animate('put down cube')

.. note::

    自定义的 animation 协程需要接受 robot 作为第一个参数，也可以有其他可选参数。

    在这个协程里，调用的机器人动作的命令也都要改成协程的调用方式，比如我们把 :data:`robot.backward(1)` 改成了 :data:`await robot.backward(1)`，把 :data:`robot.lift.height = 0` 改成了 :data:`await robot.lift.height(0)`

变脸 animation
------------------

让我们试着把前面写过的 `川剧变脸 <move.html#id5>`_ 程序改造成一个自定义动作 'bian lian'，注意比较函数和协程的区别：

.. code:: python

    import asyncio

    async def bian_lian(robot):
        robot.head.default_speed = None
        robot.lift.default_speed = 4

        for color in ['white', 'red', 'yellow', 'lightgreen']:
            await robot.head.angle(-15)
            await robot.lift.height(1)
            await robot.eyes.color(color)
            await robot.head.angle(0)
            await robot.lift.height(0)
            await asyncio.sleep(3)

    from rcute_cozmars import animations
    animations.update({'bian lian', bian_lian})

`独乐乐不如众乐乐 <https://www.zhihu.com/question/22524653/answer/574482596>`_
-------------------------------------------------------------------------------------------------

现在可以把这段代码保存到一个叫 :data:`bian_lian_animation.py` 文件中，然后把它分享给别人，别人引用你的文件后就可以在他/她的代码中使用这个动作了：

.. code:: python

    import bian_lian_animation
    from rcute_cozmars import Robot

    with Robot('xxxx') as robot:
        robot.animate('bian lian')
