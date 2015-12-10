import peewee
from peewee import *
from spydashserver.plugins import pluginmanager
import re

__all__ = peewee.__all__ + [
    'BaseModel'
]

database = SqliteDatabase('test.db')  # TODO: Load config for database


# Prefix the tables for plugins with their label
def get_table_name(model):
    try:
        prefix = pluginmanager.get_containing_pluginconfig(model).label + "_"
    except AttributeError:
        prefix = ""
    table_name = prefix + re.sub('[^\w]+', '_', model.__name__.lower())
    return table_name


# The Base for all models used by plugins
class BaseModel(Model):
    class Meta:
        database = database
        db_table_func = get_table_name


