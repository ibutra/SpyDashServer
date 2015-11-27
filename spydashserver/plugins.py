from importlib import import_module

def socketexpose(func):
    """Decorator to expose functions over websocket"""
    func.socketexposed = True
    return func


def updatetask(interval=10):
    def decorator(func):
        func.interval = interval
        func.updater = True
        return func
    return decorator


class PluginConfig(object):
    def __init__(self, label, module, models=None):
        # The label must be unique and will be used as prefix for database tables and identifier
        self.label = label

        # The root module of this plugin (NOT an instance of it)
        self.module = module

        # The module containing the model definitions
        # If this is None no models are used by the module
        self.models = models


    @classmethod
    def load(cls, name):
        # TODO: We should handle the possible exceptions here instead of just passing them on
        module = import_module(name)
        return module.plugin_config

