import cherrypy
from cherrypy.process.plugins import BackgroundTask
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from collections import deque
import importlib
import json
import SpyDashModules
from Settings import Settings


class SpyDashServer(object):
    """
    Server class for the SpyDash

    This class encapsulates all the functionality for the SpyDash server.
    It loads available modules and handles communication over Websockets
    """
    def __init__(self):
        """
        Find and load modules in the modules package
        """
        self.wsplugin = None
        self.modules = {}
        self.settings = Settings()
        self.settings.loadsettings("settings.cfg")
        importlib.invalidate_caches()
        for m in self.settings.get_modules():
            mclass = getattr(importlib.import_module("." + m, "SpyDashModules"), m)
            self.modules[m] = mclass(self)
        self.updater = BackgroundTask(5, self.update_modules)

    def start(self):
        """
        Start the server. This blocks
        """
        self.wsplugin = WebSocketPlugin(cherrypy.engine)
        self.wsplugin.subscribe()
        cherrypy.tools.websocket = WebSocketTool()

        # cherrypy.config.update({"log.access_file": "access.log",
        #                         "log.error_file": "error.log"})

        cherrypy.engine.subscribe("receive", self.receive)

        self.updater.start()
        config = {"/ws": {"tools.websocket.on": True, "tools.websocket.handler_cls": WebSocketHandler}}
        cherrypy.quickstart(self, "/", config=config)

    def broadcast(self, data):
        """
        Broadcast a message to all connected clients
        :param data: Data to broadcast
        """
        try:
            self.wsplugin.broadcast(data)
        except (AttributeError, TypeError):
            pass

    def update_modules(self):
        for module in self.modules.values():
            try:
                module.update()
            except (AttributeError, TypeError):
                pass

    def get_module(self, name):
        try:
            return self.modules[name]
        except KeyError:
            pass

    def receive(self, client, message):
        try:
            payload = json.loads(str(message))
            module_name = payload["module"]
            data = payload["data"]
            if module_name == "system":
                self.handle_system_message(client, data)
            else:
                module = self.get_module(module_name)
                try:
                    module.receive(client, data)
                except (AttributeError, TypeError):
                    pass
        except json.JSONDecodeError:
            pass

    def handle_system_message(self, client, data):
        if data["command"] == "getModules":
            response = {"module": "system",
                        "data": [name for name in self.modules.values()]}
            client.send(json.dumps(response))

    def _cp_dispatch(self, vpath):
        path = deque(vpath)
        modulename = path.popleft()
        module = self.get_module(modulename)
        if module is not None:
            return module
        else:
            return vpath

    @cherrypy.expose
    def index(self):
        return "HI"

    @cherrypy.expose
    def ws(self):
        pass


class WebSocketHandler(WebSocket):
    """
    This class will handle the interaction with a single client
    """
    def received_message(self, message):
        cherrypy.engine.publish("receive", self, message)


if __name__ == "__main__":
    server = SpyDashServer()
    server.start()

