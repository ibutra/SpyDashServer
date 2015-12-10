# SpyDashServer
Server for SpyDash

# Config
The settings.cfg File should have this form:
It consists of general Server settings and per module settings

```
{
    "plugins": [
        "weather",
        "notes"
    ],
    "plugin_settings": {
        "weather": {

            "city": "Aachen",
            "unit": "metric",
            "lang": "de"
        }
    }
}

```

# Plugins
## Pluginconfig
Plugins are python packages. The *\_\_init\_\_.py* of the package must define a *plugin_config* variable which references an instance of the *PluginConfig* class.
The pluginconfig has the following signature:
```python
PluginConfig(name, root, label=None, models=None)
```
- *name* is the full python path of the model. E.g.: 'weather'
- *root* is the class of the root class of the plugin.
- *label* an optional lable to unequily identify the plugin. This will be used in communication and as database prefix.
- *models* is the full python path to the module defining the database models for this plugin.

## Communication
The root module of a plugin can implement an *\_\_init\_\_()* function which accepts a server reference to the SpyDashServer with the *server* argument.

Plugins can implement functions that are exposed over the websocket bus. To expose a function add the socketexpose decorator:
```python
@spydashserver.socketexpose
```
Items in the *data* part of the received JSON are passed as keyword arguments to the function.
If this fails or no *data* item is available in the received message the server tries to call the function without arguments.
In case this alsow fails the server will simply ignore the received call.

Furthermore plugins can expose http endpoint over cherrypy. This is done by the known cherrypy decorator:
```python
@cherrypy.expose

```

## Periodic updates

In addition plugins can implement update functions which get called with a given interval:
```python
@spydashserver.updatetask(10)
```
The argument of the function decorator is the interval in seconds which defaults to 10 seconds.
To cancel an updater call *cancel_updater* on the server with the function as argument.
To cancel multiple updaters at once call the *cancel_updater* function with a set of updater functions to cancel.


## Database
Plugins can utilize a serverwide Database. For this [peewee](http://docs.peewee-orm.com/en/latest/) is used.
To define models subclass the *BaseModel* class from *spydashserver.datbase*. No tablenames should be given to allow the
spydashserver to inject a prefix into the table name.

# Dependencies
[(see requirements.txt)](requirements.txt)

