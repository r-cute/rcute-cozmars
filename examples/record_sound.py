from rcute_cozmars import Robot
import soundfile as sf

# 把以下 IP 地址换成你的 Cozmars 的 IP 地址
with Robot('192.168.1.102') as robot:

    # 把麦克风的音量调到 100%
    robot.microphone.volumn = 100
    print(f'麦克风输出流中每个数据块是 {robot.microphone.frame_time} 秒的音频')

    with robot.microphone as mic, sf.SoundFile('sound.wav', mode='x', samplerate=mic.samplerate, channels=mic.channels, subtype='PCM_24') as file:

        duration = 0
        for buff in mic.output_stream:
            file.write(buff)

            duration += mic.frame_time
            # 麦克风输出流中每个数据块默认是 0.1 秒的音频，录制 5 秒后结束
            if duration >= 5:
                break