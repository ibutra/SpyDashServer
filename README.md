# SpyDashServer
Server for SpyDash

#Config
The settings.cfg File should have this form:
It consists of general Server settings and per module settings

```
{
    "modules": [
        "fritzdect",
        "weather"
    ],
    "module_settings": {
        "Weather": {
            "key": "<openweathermap-key>",
            "city": "Aachen",
            "unit": "metric",
            "lang": "de"
        }
    }
}
```

#Dependencies
Current dependencies are:
- cherrypy
- ws4py
- requests (Weather module)

