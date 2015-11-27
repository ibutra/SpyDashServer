import json


class Settings(object):
    def __init__(self):
        self.settings = {}

    def loadsettings(self, filename):
        try:
            self.settings = json.load(open(filename))
        except json.JSONDecodeError:
            pass

    def get_modules(self):
        try:
            return self.settings["modules"]
        except KeyError:
            return {}

    def get_module_settings(self, module):
        try:
            return self.settings["module_settings"][module.label]
        except KeyError:
            return {}