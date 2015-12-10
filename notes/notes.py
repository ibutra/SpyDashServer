from spydashserver.decorators import socketexpose
from .models import Note
from spydashserver.settings import plugin_settings
from spydashserver.plugins import pluginmanager

class Notes(object):
    @socketexpose
    def add_note(self, text):
        note = Note(text=text)
        note.save()

    @socketexpose
    def get_notes(self):
        return [note.text for note in Note.select()]

    @socketexpose
    def get_note(self, id):
        return Note.get(id=id).text

    @socketexpose
    def remove_note(self, id):
        note = Note(id=id)
        try:
            note.delete_instance()
        except AttributeError:
            pass
