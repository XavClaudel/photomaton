import pyudev
import os

def wait_for_usb():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)

    monitor.filter_by(subsystem="block")

    for device in iter(monitor.poll, None):
        if device.action == "add":
            return device.device_node