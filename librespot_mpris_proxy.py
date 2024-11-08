#!/usr/bin/env python3

import asyncio
import logging
import os
import re
import stat

from dbus_next import BusType, PropertyAccess
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, dbus_property

_LOGGER = logging.getLogger("librespot-mpris-proxy")


class MediaPlayer2Interface(ServiceInterface):
    """MPRIS MediaPlayer2 Tnterface"""

    def __init__(self):
        super().__init__("org.mpris.MediaPlayer2")

    # Indicate we can't be controlled in any way
    @dbus_property(name="CanQuit", access=PropertyAccess.READ)
    def can_quit(self) -> "b":
        return False

    @dbus_property(name="CanSetFullscreen", access=PropertyAccess.READ)
    def can_set_fullscreen(self) -> "b":
        return False

    @dbus_property(name="CanRaise", access=PropertyAccess.READ)
    def can_raise(self) -> "b":
        return False

    @dbus_property(name="HasTrackList", access=PropertyAccess.READ)
    def has_track_list(self) -> "b":
        return False

    @dbus_property(name="Identity", access=PropertyAccess.READ)
    def identity(self) -> "s":
        return "MPRIS-Proxy"


class MediaPlayer2PlayerInterface(ServiceInterface):
    """MPRIS MediaPlayer2 Player Tnterface"""

    def __init__(self):
        super().__init__("org.mpris.MediaPlayer2.Player")

        self._playback_status = "Stopped"

    # Supported properties
    @dbus_property(name="PlaybackStatus", access=PropertyAccess.READ)
    def playback_status(self) -> "s":
        return self._playback_status

    def set_playback_status(self, val) -> None:
        if self._playback_status != val:
            self._playback_status = val
            self.emit_properties_changed(
                {"PlaybackStatus": self._playback_status})

    # Indicate we can't be controlled in any way
    @dbus_property(name="CanControl", access=PropertyAccess.READ)
    def can_control(self) -> "b":
        return False

    @dbus_property(name="CanGoNext", access=PropertyAccess.READ)
    def can_go_next(self) -> "b":
        return False

    @dbus_property(name="CanGoPrevious", access=PropertyAccess.READ)
    def can_go_previous(self) -> "b":
        return False

    @dbus_property(name="CanPlay", access=PropertyAccess.READ)
    def can_play(self) -> "b":
        return False

    @dbus_property(name="CanPause", access=PropertyAccess.READ)
    def can_pause(self) -> "b":
        return False

    @dbus_property(name="CanSeek", access=PropertyAccess.READ)
    def can_seek(self) -> "b":
        return False


async def _run():
    logging.basicConfig(
        format='%(levelname)s: %(message)s', level=logging.INFO)

    # Connect to the system bus
    _LOGGER.info("Connecting to system bus.")
    bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

    # Construct and export our interfaces
    _LOGGER.info("Exporting MediaPlayer2 interface.")
    mediaplayer2 = MediaPlayer2Interface()
    bus.export("/org/mpris/MediaPlayer2", mediaplayer2)

    _LOGGER.info("Exporting MediaPlayer2.Player interface.")
    player = MediaPlayer2PlayerInterface()
    bus.export("/org/mpris/MediaPlayer2", player)

    # Acquire our friendly name
    # TODO generate this on demand?
    name = f"org.mpris.MediaPlayer2.librespot_proxy.pid{os.getpid()}"
    _LOGGER.info(f"Requesting friendly name '{name}' on bus.")
    await bus.request_name(name)

    # Create the named pipe
    fifo = "/var/run/librespot-mpris-proxy"
    try:
        os.remove(fifo)
    except FileNotFoundError:
        pass
    os.mkfifo(fifo)
    os.chmod(fifo, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP |
             stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

    while True:
        # Blocking IO should be ok since we don't need to interact
        # with the DBus until we get an update
        with open(fifo, mode="r") as f:
            contents = f.read()

        matches = re.match("Playback Status: (\w+)", contents)
        if matches is None:
            continue

        status = matches.group(1)
        _LOGGER.info(f"Set Playback Status: {status}")
        player.set_playback_status(status)

        # Sleep to allow async tasks to run before blocking again
        # TODO might want to re-eval aiofiles
        await asyncio.sleep(1)


def main():
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
