import inspect
import json
from collections import deque
import cherrypy
from cherrypy.process.plugins import BackgroundTask
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from .plugins import socketexpose, PluginConfig
from spydashserver.settings import Settings


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
        self.worker = set()
        self.settings = Settings()
        self.settings.loadsettings("settings.cfg")
        for m in self.settings.get_modules():
            try:
                config = PluginConfig.load(m)
            except (ImportError, AttributeError):
                continue
            # Load the models and adapt them
            # TODO: implement
            # Now load the module itself
            self.modules[config.label] = config.module(server=self, label=config.label)

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
        :param module: reference to the calling module
        """
        msg = {"module": module.label, "data": data}
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
                for name, method in inspect.getmembers(module, predicate):
                    worker = BackgroundTask(method.interval, method)
                    self.worker.add(worker)
                    worker.start()
            except (TypeError, AttributeError, StopIteration):
                pass

    def cancel_updater(self, functions):
        """
        Cancel given updater functions or function
        :param functions: The updater functions to cancel, this can either be a set of functions to cancel or a singel function
        """
        try:
            workers = [worker for worker in self.worker if worker.function in functions]
        except TypeError:
            workers = [worker for worker in self.worker if worker.function == functions]
        for worker in workers:
            worker.cancel()

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
            if module_name == "system":
                attribute = getattr(self, command)
            else:
                module = self.get_module(module_name)
                attribute = getattr(module, command)
            if attribute.socketexposed is True:
                try:
                    answer = attribute(**payload["data"])
                except (KeyError, TypeError):
                    answer = attribute()
                if answer is not None:
                    msg = json.dumps({"module": module_name, "data": answer}, ensure_ascii=False)
                    client.send(msg)
        except (json.JSONDecodeError, TypeError, AttributeError, KeyError):
            return

    @socketexpose
    def get_modules(self):
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
