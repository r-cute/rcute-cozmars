from . import error, util

class Microphone(util.OutputStreamComponent):
    def __init__(self, robot, samplerate, q_size):
        util.OutputStreamComponent.__init__(self, robot)
        self._q_size = q_size
        self._samplerate = samplerate

    def _get_rpc(self):
        return self.rpc.microphone(self.samplerate, q_size=self._q_size)

    @property
    def samplerate(self):
        return self._samplerate

    @samplerate.setter
    def samplerate(self, sr):
        if not self.closed:
            raise error.CozmarsError('Cannot set samplerate while microphone is recording')
        self._samplerate = sr

