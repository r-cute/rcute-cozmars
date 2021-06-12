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
    with Robot('xxxx') as robot:

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

人脸识别
---------

Cozmars 的 :meth:`show_camera_view` 方法会启动一个后台线程打开摄像头并显示实时画面。这个方法可以和 :data:`on_camera_image` 回调函数配合使用，在每一帧画面显示之前对图像进行预处理。

另外，:data:`lastest_camera_view` 属性用来获取最新一帧的摄像头图像，:meth:`close_camera_view` 方法用来关闭摄像头画面。

下面的程序利用 rcute_ai 模块进行人脸识别。运行程序，让不同的人在摄像头前输入各自的名字，这样程序就能识别不同的人脸。

.. code:: python

    from rcute_cozmars import Robot
    import rcute_ai as ai

    # 使用 rcute_ai 的人脸识别类 FaceDetector
    face = ai.FaceDetector()

    # 定义预处理回调函数，对图像进行人脸识别和标注
    def annotate_face(img):
        fr.detect(img, annotate=True)   # 识别图像中人脸的位置和名字，并在图像中标注

    with Robot('xxxx') as robot:
        robot.show_camera_view()              # 显示摄像头图像
        robot.on_camera_image = annotate_face # 设置图像预处理的回调函数

        while True:
            i = input('输入画面中人物的名字（输入 q 结束程序）：')
            if i == 'q':
                break
            fr.memorize(name, robot.latest_camera_view)

其实，:meth:`show_camera_view` 方法在私底下所做和上一节 `获取摄像头图像 <video_audio.html#id2>`_ 里面用 :meth:`robot.camera.get_buffer` 读取摄像头数据流的办法差不多，但命令行的交互模式下直接调用 :meth:`show_camera_view` 则方便得多。

除了识别人脸，rcute_ai 模块还可以识别文字、物品、二维码、人体姿态、手势等。更多图像/语音识别的例子，请参考 `rcute-ai <https://rcute-ai.readthedocs.io>`_