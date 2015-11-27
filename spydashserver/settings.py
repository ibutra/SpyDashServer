import json


class Settings(object):
    def __init__(self):
        self.settings = {}

    def loadsettings(self, filename):
        try:
            self.settings = json.load(open(filename))
            return True
        except json.JSONDecodeError:
            print("Could not open settings file")
            return False

    def get_modules(self):
        try:
            return self.settings["modules"]
        except KeyError:
            return {}

    def get_module_settings(self, module):
        try:
            return self.settings["module_settings"][module.__class__.__name__]
        except KeyError:
            return {}