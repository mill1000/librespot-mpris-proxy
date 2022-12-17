# Librespot MPRIS Proxy
Proxy Librespot events to MPRIS D-Bus signals. Primarily intended to be used with [mpris-monitor](https://github.com/mill1000/mpris-monitor) to control external equipment.

## `librespot-mpris-proxy`
The main proxy daemon. Acquires a friendly name on the system D-Bus and emits MPRIS signals when supported events are received via a FIFO.

Usage
```
./librespot-mpris-proxy.py 
```

## `librespot-onevent`
A simple script for librespot `onevent` hook. Extracts and passes supported events to the proxy daemon via a FIFO.

Usage
```
librespot --onevent ./librespot-onevent.py 
```

## Requirements
* Python 3.6+
* [dbus-next](https://pypi.org/project/dbus-next/)