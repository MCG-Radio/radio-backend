import asyncio
import json
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst


class PlaybackController:

    def __init__(self, settings, display_controller):
        Gst.init(None)

        self.settings = settings

        self.loop = asyncio.get_event_loop()
        self.display_controller = display_controller

        self.player = Gst.ElementFactory.make('playbin', 'player')
        bus = self.player.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        bus.connect('message::tag', self._on_message)

        # auto start
        self.play(self.settings.current_index)

    def _on_message(self, bus, message):
        taglist = message.parse_tag()
        for x in range(taglist.n_tags()):
            name = taglist.nth_tag_name(x)
            if name == 'title':
                title = taglist.get_string(name)[1]
                self.loop.call_soon(self.display_controller.set_message, title)

    def play(self, index=None):
        if index is None:
            index = 1
        for radio in self.settings.radios:
            if radio['index'] == index:
                self.loop.call_soon(
                    self.display_controller.set_title, radio['label'])
                self.player.set_property('uri', radio['url'])
                self.player.set_state(Gst.State.PLAYING)

                self.settings.current_index = index
                self.settings.save()

    def stop(self):
        self.player.set_state(Gst.State.NULL)

    def next(self):
        if self.settings.current_index:
            self.stop()
            self.play(self.settings.current_index + 1)

    def previous(self):
        if self.settings.current_index:
            self.stop()
            self.play(self.settings.current_index - 1)