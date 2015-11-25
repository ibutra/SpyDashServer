# SpyDashServer
Server for SpyDash

# Config
The settings.cfg File should have this form:
It consists of general Server settings and per module settings

```
{
    "modules": [
        "FritzDECT",
        "Weather"
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

# Modules
Modules can implement functions that are exposed over the websocket bus. To expose a function add the
```python
@spydashserver.socketexpose
```
decorator.
In addition modules can implement an update function which get's called by a given interval:
```python
@spydashserver.updatetask(10)
```
The argument of the function decorator is the interval in seconds.
Furthermore modules can expose http endpoint over cherrypy. This is done by the known cherrypy decorator:
```python
@cherrypy.expose
```

#Dependencies
Current non standart lib dependencies are:
- cherrypy
- ws4py
- requests (Weather module)

