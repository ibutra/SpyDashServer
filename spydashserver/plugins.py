from importlib import import_module
from .settings import plugins


class PluginConfig(object):
    def __init__(self, name, root, label=None, models=None):
        # Python path to the Plugin e.g. 'weather'
        self.name = name

        # The root class of this plugin (NOT an instance of it)
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
            plugin = import_module(name)
            self.configs.append(plugin)

    def load_plugin_roots(self, server):
        for plugin_config in self.configs:
            plugin_config.instance = plugin_config.root(server=server)

    def get_instances(self):
        return [config.instance for config in self.configs]

    def get_containing_plugin(self, object_name):
        for plugin_config in self.configs:
            if object_name.startswith(plugin_config.name):
                return plugin_config

    def get_plugin_for_label(self, label):
        return next(config.instance for config in self.configs if config.label == label)

    def get_labels(self):
        return [config.label for config in self.configs]