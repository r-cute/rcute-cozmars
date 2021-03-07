# rcute-cozmars

Python SDK for Cozmars, the 3d printable educational robot.

中文文档: https://rcute-cozmars.readthedocs.io/

js SDK (incomplete): https://github.com/r-cute/rcute-cozmars-server/blob/master/rcute_cozmars_server/static/cozmars.js

## install

rcute-cozmars requires Python 3.7 or higher.

### Windows 64 bit

For Windows, only Python 64 bit is supported. If you also want to install [rcute-ai](https://github.com/r-cute/rcute-ai) on Windows, then you must use Python 3.7 or 3.8 version.

[download ffmpeg for windows 64bit exe files](https://ffmpeg.org/download.html#build-windows), add the extracted folder to "Path" environment variable, the extracted folder should contain 3 files named "ffprobe.exe", "ffplay.exe", and "ffmpeg.exe"

`python3 -m pip install rcute-cozmars`

### Mac OS X

```
brew install ffmpeg
python3 -m pip install rcute-cozmars
```

### Linux

```
sudo apt install ffmpeg libsndfile1
python3 -m pip install rcute-cozmars
```