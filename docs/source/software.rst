软件安装
==============

安装 Python
-------------------

首先需要安装 Python 3.7 或以上的版本。如果还没有，从 `Python 官网 <https://www.python.org/>`_ 下载并安装。

.. note::

    对于 Windows 用户，需要使用 Python *3.7 或 3.8 的 64位* 版本

安装 Cozmars Python SDK
----------------------------

针对不同的操作系统，安装步骤略有不同

Windows 64-bit
++++++++++++++++++++

.. code::

    python -m pip install rcute-cozmars

国内的小伙伴通过国内镜像服务器安装，速度更快。打开命令窗口或 PowerShell，输入下面命令：

.. code::

    python -m pip install rcute-cozmars -i https://pypi.tuna.tsinghua.edu.cn/simple

另外须 `下载 windows 64位 ffmpeg <https://ffmpeg.org/download.html#build-windows>`_ 并将路径加入 Path 环境变量，该路径下应包含 "ffprobe.exe"、"ffplay.exe"、"ffmpeg.exe" 三个文件

Mac OS X
++++++++++

.. code::

    brew install ffmpeg
    python3 -m pip install rcute-cozmars

Linux
+++++++++

.. code::

   sudo apt install ffmpeg libsndfile1
   python3 -m pip install rcute-cozmars
