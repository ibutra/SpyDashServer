import requests

class Weather(object):
    def __init__(self, server):
        self.server = server
        settings = server.settings.get_module_settings(self.__class__.__name__)
        self.apiKey = ""
        self.city = ""
        self.unit = "metric"
        self.lang = "de"
        try:
            self.apiKey = settings["key"]
            self.city = settings["city"]
        except KeyError:
            delattr(self, "update")
        try:
            self.unit = settings["unit"]
            self.lang = settings["lang"]
        except KeyError:
            pass

    def update(self):
        r = requests.get("http://api.openweathermap.org/data/2.5/weather?q=" + self.city + "&appid=" + self.apiKey + "&units=" + self.unit + "&lang=" + self.lang)
        r = r.json()
        try:
            description = r["weather"][0]["description"]
            windspeed = r["wind"]["speed"]
            winddirection = r["wind"]["deg"]
            cloudcoverage = r["clouds"]["all"]
            msg = {"description": description, "windspeed": windspeed, "winddirection": winddirection, "cloudcoverage": cloudcoverage}
            self.server.broadcast(msg, self.__class__.__name__)
        except KeyError:
            pass
