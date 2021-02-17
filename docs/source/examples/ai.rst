AI
========

“人工智能”这个词早已被滥用了。这年头，无论什么东西好像都要跟 AI 沾点边才行

嗯...咱也不例外[doge]

首先确保你已经 `安装 rcute-ai <https://rcute-ai.readthedocs.io/zh_CN/latest/installation.html>`_

语音唤醒 + 语音识别
----------------------

Cozmars 的唤醒词是 “R-Cute” 或 “阿Q”。当回调函数 :data:`when_called` 设置好后，麦克风会被打开并在后台不断监听，当检测到唤醒词时，:data:`when_called` 就会被调用。在回调函数里，你可以使用函数 :meth:`listen` 进行语音识别，得到机器人听到的语句。

下面的程序设置了 :data:`when_called` 回调函数，当你说 “阿Q” 时让机器人回答 “我在”，并根据你的命令前进或后退。

.. code:: python

    from rcute_cozmars import Robot
    with Robot() as robot:

        def cb():
            robot.say('我在')
            speech = robot.listen(lang='zh') # 如果要识别英文, 设置 lang='en'
            print(speech)
            if speech == '前进':
                robot.forward(1)
            elif speech == '后退':
                robot.backward(1)

        robot.when_called = cb

        print('按回车键结束程序')
        input()

如果要关闭麦克风和后台监听，只要把 :data:`when_called` 设置回 None

图像识别
---------

（...todo...）

以上的功能只是对 rcute-ai 的封装，更多图像/语音识别的例子，请参考 `rcute-ai <https://rcute-ai.readthedocs.io>`_