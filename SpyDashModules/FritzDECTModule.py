import asyncio


class FritzDECTModule(object):
    def __init__(self, server):
        self.server = server
        pass

    async def update(self):
        print("Hi")

    def dispatch(self, msg):
        pass
