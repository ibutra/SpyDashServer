
class FritzDECT(object):
    def __init__(self, server):
        self.server = server
        pass

    async def update(self):
        self.server.broadcast(self.__class__.__name__, ["hi","ho"])

    def dispatch(self, msg, client):
        print(msg)
