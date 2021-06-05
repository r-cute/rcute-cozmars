连接
==============

`rcute_cozmars` 是用来控制 Cozmars 机器人的 Python 模块，要使用该模块，只要在程序的开头导入它：

.. code:: python

    import rcute_cozmars

但，通常我们只需要导入 :class:`rcute_cozmars.Robot` 就行了：

.. code:: python

    from rcute_cozmars import Robot

然后以机器人的 序列号 或 IP 地址为参数新建一个 :class:`Robot` 对象，并连接机器人。也可以不指定 序列号 或 IP 地址，程序在连接时会自动搜索网络中 Cozmars 机器人，但如果搜索不到或者发现有多个机器人，则会抛出异常。

有两种连接方法：

.. raw:: html

    <style> .red {color:#E74C3C;} </style>

.. role:: red

.. raw:: html

    <style> .shell {color:#c65d09;font-weight:bold;font-size:14px} </style>

.. role:: shell

1. 使用 :red:`with` 语法，类似与文件操作，会自动建立与机器人的连接，并在 :red:`with` 以下缩进的代码块结束时自动断开连接：

    .. code:: python

        from rcute_cozmars import Robot

        # 以后均假设机器人的序列号是 'xxxx', 你需要把它换成你的 Cozmars 的序列号！
        with Robot('xxxx') as robot:
            robot.forward(2)    # 让机器人前进 2 秒


2. 显式地调用 :meth:`connect` 和 :meth:`disconnect` 方法来建立和断开连接，这种方法适合在终端窗口里用交互模式控制机器人：

    >>> from rcute_cozmars import Robot
    >>> robot = Robot() # 如果局域网中只有一个机器人，也可以不指定序列号
    >>> robot.connet()
    >>> robot.forward(2)
    >>> robot.disconnect()  # 最后记得断开连接

.. note::

    注意到以上代码开头的 :shell:`>>>`  符号了吗？它表示这些代码是在终端窗口里输入的命令；

    而 *没有* :shell:`>>>` 符号的代码块则表示文件中的整段代码

.. note::

    一个 Cozmars 机器人同时只能与一个程序连接，只有断开连接之后才能接受下一个程序的连接


.. seealso::

    `rcute_cozmars.Robot.connect <../api/robot.html#rcute_cozmars.robot.Robot.connect>`_ ， `rcute_cozmars.Robot.disconnect <../api/robot.html#rcute_cozmars.robot.Robot.disconnect>`_