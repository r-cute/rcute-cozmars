连接
==========

rcute_cozmars 是用来控制 Cozmars 机器人的 Python 模块，要使用该模块，首先要在该程序的开头引用它：

.. code:: python

	from rcute_comzars import Robot

然后以机器人的 序列号 或 IP 地址为参数新建一个 :class:`Robot` 对象，并连接机器人。有两种连接方法：

.. red:: html

	<style>.red{color:red}</style>

1. 使用 :red:`with` 语法，类似与文件操作，会自动建立与机器人的连接，并在 :red:`with` 以下缩进的代码块结束时自动断开连接：

.. code:: python

	from rcute_cozmars import Robot

	with Robot('192.168.1.102') as robot:
		robot.forward(2)	# 让机器人前进 2 秒


2. 显示地调用 :meth:`connect` 和 :meth:`disconnect` 方法来建立和断开连接，这种方法适合在命令行里用交互的方式控制机器人：

	>>> from rcute_cozmars import Robot
	>>> robot = Robot('192.168.1.102')
	>>> robot.connet()
	>>> robot.forward(2)
	>>> robot.disconnect()	# 最后记得断开连接

.. note::

	一个 Cozmars 机器人同时只能与一个程序连接，该程序断开连接之后下一个程序才能建立连接


