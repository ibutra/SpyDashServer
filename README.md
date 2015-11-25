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
Modules must implement an *__init__()* function which accepts a server reference to the SpyDashServer with the *server* argument.

Modules can implement functions that are exposed over the websocket bus. To expose a function add the socketexpose decorator:
```python
@spydashserver.socketexpose
```
Items in the *data* part of the received JSON are passed as keyword arguments to the function.
If this fails or no *data* item is available in the received message the server tries to call the function without arguments.
In case this alsow fails the server will simply ignore the received call.


In addition modules can implement update functions which get called with a given interval:
```python
@spydashserver.updatetask(10)
```
The argument of the function decorator is the interval in seconds which defaults to 10 seconds.
To cancel an updater call *cancel_updater* on the server with the function as argument.
To cancel multiple updaters at once call the *cancel_updater* function with a set of updater functions to cancel.

Furthermore modules can expose http endpoint over cherrypy. This is done by the known cherrypy decorator:
```python
@cherrypy.expose
```

# Dependencies
Current non standart lib dependencies are:
- cherrypy
- ws4py
- requests (Weather module)

