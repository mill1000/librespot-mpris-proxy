#! /bin/env python3

import os
import stat

SUPPORTED_EVENTS = {
    "stopped": "Stopped",
    "playing": "Playing",
    "paused": "Paused"
}

event = os.environ['PLAYER_EVENT']

if event not in SUPPORTED_EVENTS:
    print(f"Received unsupported event: '{event}'.")
    exit()

# Fetch DBus version of event
dbus_event = SUPPORTED_EVENTS[event]
print(f"Received librespot event: '{event}' -> '{dbus_event}'.")

fifo = "/tmp/librespot-dbus"

if stat.S_ISFIFO(os.stat(fifo).st_mode) is False:
  print(f"{fifo} is not a named pipe.")
  exit(1)

with open(fifo, "a") as f:
  print(f"Playback Status: {dbus_event}", file=f)

exit()