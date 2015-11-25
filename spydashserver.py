import cherrypy
from cherrypy.process.plugins import BackgroundTask
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from collections import deque
import importlib
import json
import SpyDashModules
import inspect
from settings import Settings


def socketexpose(func):
    """Decorator to expose functions over websocket"""
    func.socketexposed = True
    return func


def updatetask(interval):
    def decorator(func):
        func.interval = interval
        func.updater = True
        return func
    return decorator


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

        self.start_updater()

        config = {"/ws": {"tools.websocket.on": True, "tools.websocket.handler_cls": WebSocketHandler}}
        cherrypy.quickstart(self, "/", config=config)

    def broadcast(self, data, module):
        """
        Broadcast a message to all connected clients
        :param data: Data to broadcast
        """
        msg = {"module": module, "data": data}
        try:
            msg = json.dumps(msg, ensure_ascii=False)
        except TypeError:
            return
        self.wsplugin.broadcast(msg)

    def start_updater(self):
        def predicate(x):
            try:
                return x.updater
            except (TypeError, AttributeError):
                return False

        for module in self.modules.values():
            try:
                method = next(iter(inspect.getmembers(module, predicate)))
                method = method[1]
                BackgroundTask(method.interval, method).start()
            except (TypeError, AttributeError, StopIteration):
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
            command = payload["command"]
            data = payload["data"]
            if module_name == "system":
                attribute = getattr(self, command)
                if attribute.socketexposed is True:
                    answer = attribute(data)
            else:
                module = self.get_module(module_name)
                attribute = getattr(module, command)
                if attribute.socketexposed is True:
                    answer = attribute(data)
            if answer is not None:
                msg = json.dumps({"module": module_name, "data": answer}, ensure_ascii=False)
                client.send(msg)
        except (json.JSONDecodeError, TypeError, AttributeError):
            return

    @socketexpose
    def get_modules(self, data):
        response = [name for name in self.modules.keys()]
        return response

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
