import cherrypy
from cherrypy.process.plugins import BackgroundTask
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
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
        self.wsplugin = None
        self.modules = []

        config = json.load(open("config"))
        importlib.invalidate_caches()
        for m in config["modules"]:
            mclass = getattr(importlib.import_module("." + m, "SpyDashModules"), m)
            if hasattr(mclass, "dispatch"):
                self.modules.append(mclass(self))
        self.updater = BackgroundTask(1, self.update_modules)

    def start(self):
        """
        Start the server. This blocks
        """
        self.wsplugin = WebSocketPlugin(cherrypy.engine)
        self.wsplugin.subscribe()
        cherrypy.tools.websocket = WebSocketTool()

        self.updater.start()
        cherrypy.quickstart(self, "/", config={"/ws": {
            "tools.websocket.on": True,
            "tools.websocket.handler_cls": WebSocketHandler
        }})

    def broadcast(self, data):
        """
        Broadcast a message to all connected clients
        :param data: Data to broadcast
        """
        self.wsplugin.broadcast(data)

    def update_modules(self):
        for module in self.modules:
            if hasattr(module, "update"):
                module.update()

    @cherrypy.expose
    def index(self):
        return "HI"

    @cherrypy.expose
    def ws(self):
        handler = cherrypy.request.ws_handler
        pass


class WebSocketHandler(WebSocket):
    """
    This class will handle the interaction with a single client
    """
    def received_message(self, message):
        pass


if __name__ == "__main__":
    server = SpyDashServer()
    server.start()

