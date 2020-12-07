Bb can do it
=================

    >>> robot.buzzer.play([500, 500])

The above command makes the robot emit two 500Hz syllables

The :data:`buzzer` attribute of :class:`Robot` represents a buzzer inside the robot. The buzzer can vibrate at different frequencies to emit different `tones`.

.. |Tone| raw:: html

    <a href='https://gpiozero.readthedocs.io/en/stable/api_tones.html' target='blank'>gpiozero.tones.Tone</a>

.. note::

    The `tone` mentioned here can be represented by different data types in the program.

    For example, the do sound in C major do re me fa so la si, the music symbol is `'C4'`, the frequency is 261.63 Hz, and the MIDI code is #60, then `'C4'`, `261.63` and `60 `Can be used to represent this tone, or it can be represented by |Tone| object

    Use `None` or `0` to indicate mute

Just change the :data:`tone` property of :data:`buzzer` to change the tone of the buzzer:

    >>> from gpiozero.tones import Tone
    >>> # The following four sentences have the same effect, so you won't hear the change in pitch. Try to change the frequency or music mark and listen again:
    >>> robot.buzzer.tone = 261.63
    >>> robot.buzzer.tone ='C4'
    >>> robot.buzzer.tone = 60
    >>> robot.buzzer.tone = Tone('C4')
    >>> # Mute:
    >>> robot.buzzer.quiet() # or:
    >>> robot.buzzer.tone = 0

A more convenient way to play a single `tone` is to use the :meth:`set_tone` method of :data:`buzzer` to set both the `tone` and the playing time:

    >>> robot.buzzer.set_tone('A4', duration=2)

Hum
---------------

You can use the :meth:`play` method of :data:`buzzer` to play a piece of music. The parameter of :meth:`play` is an array of `tones`. By default, each `tone` is one beat, and the `tones` surrounded by brackets are each half beat, and `notes surrounded by two layers of brackets. `Each is 1/4 beat... and so on, the beats of each additional layer of brackets are halved; in addition, the :data:`tempo` parameter is used to specify the playback speed (BPM)

Run the following program to guess which Jay Chou song is:

.. code:: python

    from rute_cozmars import Robot

    song = ['D4','G4','G4','B4','C5','B4','A4',
            ('G4','A4'),'B4','B4','B4','B4', ('A4','B4'),'A4','G4']

    with Robot('0a3c') as robot:
        robot.buzzer.play(song, tempo=120)

.. seealso::

    `rcute_cozmars.buzzer <../api/buzzer.html>`_