from importlib import import_module
from .settings import plugins


class PluginConfig(object):
    def __init__(self, name, root, label=None, models=None):
        # Python path to the Plugin e.g. 'weather'
        self.name = name

        # The python path to the root class of this plugin relative to name
        self.root = root

        # The label must be unique and will be used as prefix for database tables and identifier
        # If no label is set the python path wil be used
        if label:
            self.label = label
        else:
            self.label = name

        # The module containing the model definitions e.g. "notes.models"
        # If this is None no models are used by the module
        self.models = models

    @classmethod
    def load(cls, name):
        # TODO: We should handle the possible exceptions here instead of just passing them on
        module = import_module(name)
        return module.plugin_config


class PluginManager(object):

    def __init__(self):
        self.configs = []

    def load_configs(self):
        for name in plugins:
            self.configs.append(PluginConfig.load(name))

    def load_plugin_roots(self, server):
        for plugin_config in self.configs:
            module = import_module(plugin_config.name + '.' + plugin_config.root[:plugin_config.root.rfind(".")])
            try:
                root = getattr(module, plugin_config.root[plugin_config.root.rfind('.') + 1:])
            except AttributeError:
                continue
            try:  # Try to pass a reference to server
                plugin_config.instance = root(server=server)
            except TypeError:
                plugin_config.instance = root()

    def load_models(self):
        for plugin_config in self.configs:
            try:
                import_module(plugin_config.models)
            except AttributeError:
                pass

    def get_instances(self):
        return [config.instance for config in self.configs]

    def get_containing_pluginconfig(self, object):
        object_name = object.__module__
        for plugin_config in self.configs:
            if object_name.startswith(plugin_config.name):
                return plugin_config

    def get_containing_pluginlabel(self, object):
        return self.get_containing_pluginconfig(object).label

    def get_plugin_for_label(self, label):
        return next(config.instance for config in self.configs if config.label == label)

    def get_labels(self):
        return [config.label for config in self.configs]

pluginmanager = PluginManager()