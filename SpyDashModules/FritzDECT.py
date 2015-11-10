
class FritzDECT(object):
    def __init__(self, server):
        self.server = server
        pass

    def update(self):
        pass

    def receive(self, client, data):
        print(data)
