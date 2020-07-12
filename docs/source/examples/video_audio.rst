摄像头和麦克风
=========================

屏幕下方的“樱桃小嘴”其实才是 Cozmars 的眼睛，这是一颗 500W 像素的摄像头；而 Cozmars 的耳朵（麦克风）奇怪地长在它的背上，就是按钮旁边那个小圆点。通过摄像头和麦克风回传数据，图像识别、语音识别等更有趣的玩法也成为可能

:class:`Robot` 的 :data:`camera` 和 :data:`microphone` 分别用来操作摄像头和麦克风，他们都是流设备，使用方法也类似。
需要先调用 :meth:`open` 方法打开设备，才能用  :meth:`read` 方法读取输出流中的数据，最后要调用 :meth:`close` 方法关闭设备。

读取摄像头
---------------

下面的程序通过获取摄像头的实时画面，让我们用 Cozmars 的视角观察世界：

.. code:: python

    from rcute_cozmars import Robot
    import cv2

    # 把以下 IP 地址换成你的 Cozmars 的 IP 地址
    with Robot('192.168.1.102') as robot:

        robot.camera.open()

        print('按下任意键退出')
        while True:
            frame = robot.camera.read()
            cv2.imshow('cozmars camera', frame)
            if cv2.waitKey(1) > 0:
                break

        robot.camera.close()

    cv2.destroyAllWindows()

.. raw:: html

    <style> .red {color:#E74C3C;} </style>

.. role:: red

打开、读取、关闭，是不是很像对文件的操作？也许你猜到了，:data:`camera` 和 :data:`microphone` 也可以利用 :red:`with` 语法来帮助我们自动打开和关闭，甚至还可以使用更优雅的 :red:`for ... in ...` 的语法来代替 :red:`while` 循环。因此，上面的代码可以改为：

.. code:: python

    from rcute_cozmars import Robot
    import cv2

    # 把以下 IP 地址换成你的 Cozmars 的 IP 地址
    with Robot('192.168.1.102') as robot:

        with robot.camera:

            print('按下任意键退出')
            for frame in robot.camera:
                cv2.imshow('cozmars camera', frame)
                if cv2.waitKey(1) > 0:
                    break

    cv2.destroyAllWindows()

随便提一下，:data:`camera` 可以通过 :data:`framerate` 和 :data:`resolution` 属性来改变帧率和分辨率

读取麦克风
--------------

用 :red:`with` 和 :red:`for ... in ...` 语法来演示一下如何获取麦克风数据，下面的程序从麦克风数据流中读取数据并保存成一段 5 秒的录音文件。


.. code:: python

    from rcute_cozmars import Robot
    import soundfile as sf

    # 把以下 IP 地址换成你的 Cozmars 的 IP 地址
    with Robot('192.168.1.102') as robot:

        # 把麦克风的音量调到 100%
        robot.microphone.volumn = 100

        print(f'麦克风输出流中每个数据块是 {robot.microphone.frame_time} 秒的音频')

        with robot.microphone as mic, sf.SoundFile('sound.wav', mode='b', samplerate=mic.samplerate, channels=mic.channels, subtype='PCM_24') as file:

            duration = 0
            for buff in mic:
                file.write(buff)

                duration += mic.frame_time
                # 麦克风输出流中每个数据块默认是 0.1 秒的音频，录制 5 秒后结束
                if duration >= 5:
                    break


这个程序需要 soundfile 模块用来操作声音文件，如果没有安装 soundfile ，可以在命令行输入 `pip install soundfile` 安装

如果细心的话，你会注意到程序中用到了 :data:`microphone` 的几个属性： :data:`volumn` 用来调节麦克风的音量大小， :data:`samplerate` 、 :data:`channels` 和 :data:`frame_time` 分别是麦克风的采样率、声道数和每次从输出流中读取的数据块的时长。除了音量外，这些属性通常不需要修改。

.. seealso::

	`rcute_cozmars.camera <../api/camera.html>`_ ， `rcute_cozmars.microphone <../api/microphone.html>`_

以上演示了如何从麦克风和摄像头中读取数据，有了图像和声音数据，我们就可以做诸如图像识别、语音识别这样更好玩的实验，有兴趣的请参考 |rcute-ai|

.. |rcute-ai| raw:: html

   <a href='https://rcute-ai.readthedocs.io' target='blank'>rcute-ai</a>
