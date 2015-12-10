from spydashserver.plugins import PluginConfig
from .notes import Notes

plugin_config = PluginConfig("notes", Notes, models='notes.models')
