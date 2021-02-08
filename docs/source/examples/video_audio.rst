看和听
============

其实，屏幕下方的“樱桃小嘴”才是 Cozmars 的眼睛，这是一颗 500W 像素的摄像头；而 Cozmars 的耳朵（麦克风）奇怪地长在它的背上，嗯，就是按钮旁边那个小圆点。

通过摄像头和麦克风，我们就能以 Cozmars 的视角“观海听 `Tao <https://github.com/yikeke/tao-of-programming>`_ ”，图像识别、语音识别等更有趣的玩法也成为可能

.. raw:: html

    <style> .red {color:#E74C3C;} </style>

.. role:: red

:class:`Robot` 的 :data:`camera` 和 :data:`microphone` 分别用来操作摄像头和麦克风，他们都是流设备，使用方法也类似。
需要先调用 :meth:`get_buffer` 获得数据流，然后利用 :red:`with` 语法来帮助我们自动打开和关闭数据流。

读取摄像头
---------------

下面的程序通过获取摄像头的实时画面，让我们用 Cozmars 的视角观察世界：

.. code:: python

    from rcute_cozmars import Robot
    import cv2

    # 把以下序列号换成你的 Cozmars 的序列号
    with Robot() as robot:

        with robot.camera.get_buffer() as cam_buf:
            print('按下任意键退出')

            for frame in cam_buf:
                cv2.imshow('cozmars camera', frame)
                if cv2.waitKey(1) > 0:
                    break

    cv2.destroyAllWindows()

当摄像头没有在传输视频时，也可以用 :meth:`capture` 方法拍张照

    >>> robot.camera.capture('./photo.jpeg')

随便提一下，:data:`camera` 可以通过 :data:`frame_rate` 和 :data:`resolution` 属性来改变帧率和分辨率

读取麦克风
--------------

用 :red:`with` 和 :red:`for ... in ...` 语法来演示一下如何获取麦克风数据，下面的程序从麦克风数据流中读取数据并保存成一段 5 秒的录音文件。


.. code:: python

    from rcute_cozmars import Robot
    import wave

    # 把以下序列号换成你的 Cozmars 的序列号
    with Robot() as robot:
        mic = robot.microphone

        with mic.get_buffer() as mic_buf, wave.open('record.wav', 'wb') as file:
            file.setnchannels(1)
            file.setframerate(mic.sample_rate)
            file.setsampwidth(mic.sample_width)

            duration = 0
            for segment in mic_buf:
                file.writeframesraw(segment.raw_data)

                # 麦克风输出流中每个数据块默认是 0.1 秒的音频，录制 5 秒后结束
                duration += segment.duration_seconds
                if duration >= 5:
                    break

:data:`microphone` 还有几个属性： :data:`volume` 和 :data:`gain` 用来调节麦克风的音量大小， :data:`sample_rate` 、 :data:`dtype` 和 :data:`block_duration` 分别是麦克风的采样率、数据类型和每次从输出流中读取的数据块的时长。除了音量增益 :data:`gain` 以外，这些属性通常不需要修改。

.. seealso::

	`rcute_cozmars.camera <../api/camera.html>`_ ， `rcute_cozmars.microphone <../api/microphone.html>`_

以上演示了如何从麦克风和摄像头中读取数据，有了图像和声音数据，我们就可以做诸如图像识别、语音识别这样更好玩的实验，有兴趣的请参考 |rcute-ai|

.. |rcute-ai| raw:: html

   <a href='https://rcute-ai.readthedocs.io' target='blank'>rcute-ai</a>
