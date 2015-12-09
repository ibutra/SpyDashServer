from peewee import BaseModel, with_metaclass
from peewee import *
from .plugins import pluginmanager

__all__ = [
    'ModelBase',
]

database = SqliteDatabase('test.db')  #TODO: Load config for database


class ModelMeta(BaseModel):
    def __new__(cls, *args, **kwargs):
        cls = super(ModelMeta, cls).__new__(cls, *args, **kwargs)
        prefix = pluginmanager.get_containing_pluginconfig(cls).label
        cls._meta.db_table = prefix + "_" + cls._meta.db_table
        return cls


class ModelBase(with_metaclass(ModelMeta)):
    class Meta:
        database = database
