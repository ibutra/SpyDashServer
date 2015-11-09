from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import importlib
import json
import SpyDashModules
import asyncio


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
        self.factory = None
        self.loop = None
        self.modules = []
        config = json.load(open("config"))
        importlib.invalidate_caches()
        for m in config["modules"]:
            mclass = getattr(importlib.import_module("." + m, "SpyDashModules"), m)
            if hasattr(mclass, "dispatch"):
                self.modules.append(mclass(self))

    def start(self):
        """
        Start the WebSocket server
        """
        self.factory = SpyDashServerFactory(self, u"ws://127.0.0.1:8080")
        self.factory.protocol = SpyDashServerProtocol
        self.loop = asyncio.get_event_loop()
        coro = self.loop.create_server(self.factory, port=8080)
        server = self.loop.run_until_complete(coro)

        self.loop.call_soon(self.updateFunction)

        self.loop.run_forever()

    def stop(self):
        self.loop.stop()
        self.loop.close()

    def dispatch(self, msg, client):
        """
        Dispatch received message to applicable module or handle directly

        :param msg: The received json message
        """
        data = msg["data"]
        target = msg["module"]
        if target == "system":
            self.handleSystemMessage(data, client)
        else:
            try:
                m = [module for module in self.modules if module.__class__.__name__ == target][0]
                m.dispatch(data, client)
            except IndexError:
                pass

    def broadcast(self, data):
        """
        Send a broadcast message to all connected clients

        :param data: The data to broadcast. This will be wrapped in a JSON
        """
        # TODO: build the JSON
        if self.factory is not None:
            self.factory.broadcast(data)

    def send(self, data, client):
        """
        Sends data to the given client
        :param data: The data to send
        :param client: The intended recipient
        """
        payload = {"module":"system", "data":data}
        payload = json.dumps(payload, ensure_ascii=False)
        client.sendMessage(payload.encode("utf-8"), isBinary=False)

    def updateFunction(self):
        """
        This function calls itself through the loop every second and calls the update functions of al modules
        """
        for m in self.modules:
            if hasattr(m, "update"):
                self.loop.create_task(m.update())
        self.loop.call_later(1, self.updateFunction)

    def handleSystemMessage(self, data, client):
        """
        Handle all system messages
        :param data: The data part of the received json
        """
        command = data["command"]
        if command == "getModules":
            data = {"modules": [m.__class__.__name__ for m in self.modules]}
            self.send(data, client)



class SpyDashServerProtocol(WebSocketServerProtocol):
    """
    The websocket protocoll for communication with clients
    """

    def __init__(self):
        super().__init__()

    def onOpen(self):
        self.factory.register(self)

    def onClose(self, wasClean, code, reason):
        self.factory.unregister(self)

    def onMessage(self, payload, isBinary):
        try:
            self.factory.spydashserver.dispatch(json.loads(payload.decode('utf-8')), self)
        except json.JSONDecodeError:
            print("Failed to decode message")



class SpyDashServerFactory(WebSocketServerFactory):
    """
    The websocket server factory to enable broadcasting
    """
    def __init__(self, spydashserver, url=None):
        super().__init__(url=url)
        self.spydashserver = spydashserver
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
    server = SpyDashServer()
    server.start()

