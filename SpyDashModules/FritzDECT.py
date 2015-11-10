
class FritzDECT(object):
    def __init__(self, server):
        self.server = server
        pass

    def update(self):
        self.server.broadcast("test")

    def dispatch(self, msg, client):
        print(msg)
