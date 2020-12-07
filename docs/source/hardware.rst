Robot and Rubik's cube settings
===================

Power on/off
----------------
Power on: Press the black power button on the *side* of the Cozmars robot. If the yellow light inside the head is on, it means that Cozmars has started. The start-up process takes about tens of seconds to one minute, and the start-up is complete with a beep. At this time, if you click the button on the *top*, Cozmars's *four-digit serial number* will appear on the screen

Shutdown: Press and hold the *top* button for about 5 seconds, and you will hear a beep to shut down. Wait for the yellow light in the head to go out and then press the power button on the *side* to disconnect the power.

Turning on/off the Rubik's Cube is much simpler. Press the black power button when starting up, and then press it again if you want to shut down.

.. note::

    Since the Cozmars robot is controlled by the raspberry pi zero w, it runs the raspbian operating system, just like a computer, it is best to shut down the operating system before powering off when shutting down; while the Cube is controlled by the ESP8266 single-chip microcomputer, it does not need to be shut down. Be particular

wifi settings
-----------

Cozmars: Since the wifi has not been set up for the first time, it will provide a wifi hotspot named :data:`rcute-cozmars-xxxx` by default, where :data:`xxxx` is the serial number of Cozmars. Connect to this wifi hotspot, enter the password: data:`xxxxxxxx` (ie the serial number twice), then use the browser to visit: data:`http://rcute-cozmars-xxxx.local`, click: data:`wifi settings `Button, enter the wifi name and password of the home or office environment, and click save. After restarting the network, the robot can automatically connect to the wifi just set.

Rubik's Cube: Similar to Cozmars, if wifi is not set, Rubik's Cube will provide a wifi hotspot named: data:`rcute-cube-****` when starting, where: data:`****` is Rubik's cube Serial number (different from Cozmars serial number), after connecting to the wifi hotspot, enter: data:`********` twice the serial number as the password, then visit: data:`http://rcute-cube -****.local` can set wifi.

Cozmars and Rubik's Cube will first try to connect to the set wifi every time they start, and if they cannot connect, they will provide the default wifi hotspot.


Recharge
------------

Put Cozmars or Rubik's Cube on the charger to charge. When the charger's light turns green, it means it is fully charged. If there are problems such as unable to turn on, restarting without reason, abnormal connection, etc., it is likely to be caused by insufficient power. Try again after charging.

It is recommended to fully charge before each use, so as to ensure that it can be used for a long time.


Firmware upgrade
----------------

The firmware updates of Cozmars and Rubik's Cube are pushed through the Internet. When connected to the Internet, use a browser to visit the Cozmars page: data:`http://rcute-cozmars-xxxx.local` or the Rubik's Cube page: data:`http://rcute -cube-****.local`, when the :data:`update` button appears, it means there is a new version of the firmware, click the button to update the firmware


Servo debugging
----------
The head and left and right arms of the Cozmars robot are driven by three servos respectively. When the head or arms cannot move to the specified position, or the left and right arms are not synchronized, you can visit: data:`http://rcute- cozmars-xxxx.local` page, click the :data:`Servo debugging` button to debug
(... to be continued...)

Motor debugging
----------
The left and right wheels of the Cozmars robot are driven by two motors. When Cozmars cannot go straight when moving forward or backward, you can visit the page: data:`http://rcute-cozmars-xxxx.local`, click: data:`motor debugging `Button to debug

(... to be continued...)