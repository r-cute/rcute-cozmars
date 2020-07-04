# record sound from microphone for 5 seconds and save to file
# requires soundfile module

from rcute_cozmars import Robot
import soundfile as sf

# replace ip address with your cozmars' ip
with Robot('192.168.1.102') as robot:

    # set record volumn to 100%, volumn changes will be saved even after reboot
    robot.microphone.volumn = 100

    with robot.microphone as mic, sf.SoundFile('sound.wav', mode='x', samplerate=mic.samplerate, channels=mic.channels, subtype='PCM_24') as file:

        count = 0
        for buff in mic.output_stream:
            file.write(buff)

            # every buffer is 0.1 second
            count += 1
            if count == 50:
                break