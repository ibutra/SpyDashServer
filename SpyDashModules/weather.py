import requests
from datetime import datetime, timedelta


class Weather(object):
    def __init__(self, server):
        self.server = server
        settings = server.settings.get_module_settings(self.__class__.__name__)
        self.apiKey = ""
        self.city = "Aachen"
        self.unit = "metric"
        self.lang = "de"
        self.lastMessage = {}
        try:
            self.apiKey = settings["key"]
        except KeyError:
            delattr(self, "update")  # We remove our update function if we don't have an api key because we obviously can't update in this cas
        try:
            self.city = settings["city"]
            self.unit = settings["unit"]
            self.lang = settings["lang"]
        except KeyError:
            pass

    def update(self):
        arguments = {"q": self.city, "appid": self.apiKey, "units": self.unit, "lang": self.lang}
        r = requests.get("http://api.openweathermap.org/data/2.5/weather", params=arguments)
        try:
            r = r.json()
        except ValueError:
            return
        try:
            description = r["weather"][0]["description"]
            windspeed = r["wind"]["speed"]
            winddirection = r["wind"]["deg"]
            cloudcoverage = r["clouds"]["all"]
            temp = r["main"]["temp"]
            humidity = r["main"]["humidity"]
            msg = {"description": description, "windspeed": windspeed, "winddirection": winddirection, "cloudcoverage": cloudcoverage, "temp": temp, "humidity": humidity}
            # Time to get the forecast
            r = requests.get("http://api.openweathermap.org/data/2.5/forecast", params=arguments)
            try:
                r = r.json()
            except ValueError:
                pass
            try:
                forecastlist = r["list"]
                forecastlist = [{"temp": forecast["main"]["temp"], "description": forecast["weather"][0]["description"], "time": forecast["dt"]} for forecast in forecastlist if datetime.utcfromtimestamp(forecast["dt"]) < datetime.utcnow() + timedelta(days=1)]  # Only take the forecast for the next day
                msg["forecast"] = forecastlist
            except KeyError:
                pass
            if msg != self.lastMessage:
                self.server.broadcast(msg, self.__class__.__name__)
                self.lastMessage = msg
        except KeyError:
            pass
