from . import util
import json

class Env(util.Component):
    """
    Helper class to set/get env-vars on server side.

    These env-vars are different from conf-vars(saved in /home/pi/.cozmars.conf.json) in that env-vars are specific to individual servers, but are used on client side,
    while conf-vars are unknown to client.
    """
    def __init__(self, robot):
        util.Component.__init__(self, robot)

    @util.mode()
    async def get(self, name):
        """ """
        return await self._rpc.get_env(name)

    @util.mode()
    async def load(self):
        """ """
        self.vars = json.loads(await self._robot._get('/env'))

    @util.mode()
    async def rm(self, name):
        """remove"""
        await self._rpc.del_env(name)
        self.vars.pop(name)

    @util.mode()
    async def set(self, name, value):
        """ """
        await self._rpc.set_env(name, value)
        self.vars[name] = value

    @util.mode()
    async def save(self):
        """save to /home/pi/.cozmars.env.json on Rpi zero"""
        return await self._rpc.save_env()
