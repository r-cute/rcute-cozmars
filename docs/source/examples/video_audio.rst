Watch and listen
============

In fact, the "cherry mouth" at the bottom of the screen is Cozmars' eyes, which is a 500W pixel camera; and Cozmars' ears (microphone) are strangely growing on its back, well, it is the small dot next to the button .

Through the camera and microphone, we can "watch the sea and listen to `Tao <https://github.com/yikeke/tao-of-programming>`_" from the perspective of Cozmars. More interesting gameplay such as image recognition and voice recognition are also available. become possible

.. raw:: html

    <style> .red {color:#E74C3C;} </style>

.. role:: red

The :data:`camera` and :data:`microphone` of :class:`Robot` are used to operate the camera and the microphone respectively. They are all streaming devices and the methods of use are similar.
You need to call :meth:`get_buffer` to get the data stream first, and then use the :red:`with` syntax to help us automatically open and close the data stream.

Read camera
---------------

The following program allows us to observe the world from the perspective of Cozmars by obtaining the real-time image of the camera:

.. code:: python

    from rcute_cozmars import Robot
    import cv2

    # Replace the following serial number with your Cozmars serial number
    with Robot('0a3c') as robot:

        with robot.camera.get_buffer() as cam_buf:
            print('Press any key to exit')

            for frame in cam_buf:
                cv2.imshow('cozmars camera', frame)
                if cv2.waitKey(1)> 0:
                    break

    cv2.destroyAllWindows()

When the camera is not transmitting video, you can also use the :meth:`capture` method to take a picture

     >>> robot.camera.capture('./photo.jpeg')

By the way, :data:`camera` can use :data:`frame_rate` and :data:`resolution` properties to change the frame rate and resolution

Read microphone
--------------

Use :red:`with` and :red:`for ... in ...` syntax to demonstrate how to get microphone data. The following program reads data from the microphone data stream and saves it as a 5-second recording file .


.. code:: python

    from rcute_cozmars import Robot
    import soundfile as sf
    import numpy as np

    # Replace the following serial number with your Cozmars serial number
    with Robot('0a3c') as robot:
        mic = robot.microphone

        print(f'Volume gain {mic.gain}')

        with mic.get_buffer() as mic_buf, sf.SoundFile('sound.wav', mode='w', samplerate=mic.sample_rate, channels=mic.channels, subtype='PCM_24') as file:

            duration = 0
            for segment in mic_buf:
                data = np.frombuffer(segment.raw_data, dtype=mic.dtype)
                file.write(data)

                # Each data block in the microphone output stream is 0.1 seconds of audio by default, and the recording ends after 5 seconds
                duration += segment.duration_seconds
                if duration >= 5:
                    break


(This program needs the |soundfile| module to save sound files. If the soundfile is not installed, you can enter: data:`python3 -m pip install soundfile` on the command line to install it. If it is a Linux system, enter: data:` sudo apt-get install libsndfile1` manually install libsndfile)


.. |soundfile| raw:: html

   <a href='https://pysoundfile.readthedocs.io/en/0.10.0/' target='blank'>soundfile</a>


:data:`microphone` also has several attributes: :data:`volume` and :data:`gain` are used to adjust the volume of the microphone, :data:`sample_rate`, :data:`channels` and :data: `block_duration` is the sampling rate of the microphone, the number of channels, and the duration of each data block read from the output stream. Except for the volume gain :data:`gain`, these properties usually do not need to be modified.

.. seealso::

`rcute_cozmars.camera <../api/camera.html>`_, `rcute_cozmars.microphone <../api/microphone.html>`_

The above demonstrates how to read data from the microphone and camera. With image and sound data, we can do more fun experiments such as image recognition and speech recognition. If you are interested, please refer to |rcute-ai|

.. |rcute-ai| raw:: html

   <a href='https://rcute-ai.readthedocs.io' target='blank'>rcute-ai</a>