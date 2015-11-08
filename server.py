from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import importlib
import json
import SpyDashModules


class SpyDashServer(object):
    """
    Server class for the SpyDash

    This class encapsules all the functionality for the SpyDash server.
    It loads available modules and handles communication over Websockets
    """
    def __init__(self):
        """
        Find and load modules in the modules package
        """
        self.modules = []
        config = json.load(open("config"))
        importlib.invalidate_caches()
        for m in config["modules"]:
            mClass = getattr(importlib.import_module("." + m, "SpyDashModules"), m)
            if hasattr(mClass, "run") and hasattr(mClass, "dispatch"):
                self.modules.append(mClass(self))

    def dispatch(self, msg):
        """
        Dispatch received message to applicable module or handle directly

        :param msg: The received json message
        """
        pass


class SpyDashServerProtocol(WebSocketServerProtocol):
    """
    The websocket protocoll for communication with clients
    """

    def __init__(self, spyDashServer):
        super().__init__()
        self.server = spyDashServer

    def onOpen(self):
        self.factory.register(self)

    def onClose(self, wasClean, code, reason):
        self.factory.unregister(self)

    def onMessage(self, payload, isBinary):
        self.server.dispatch(json.loads(payload.decode('utf-8')))


class SpyDashServerFactory(WebSocketServerFactory):
    """
    The websocket server factory to enable broadcasting
    """
    def __init__(self, url=None):
        super().__init__(self, url)
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg, isBinary=False):
        prepared = self.prepareMessage(msg, isBinary=isBinary)
        for c in self.clients:
            c.sendPreparedMessage(prepared)
        print("Message sent")

if __name__ == "__main__":
    b = SpyDashServer()
