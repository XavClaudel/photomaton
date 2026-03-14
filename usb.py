import os
import psutil
import time
import shutil
from datetime import date
from config import *




def detect_existing_usb():

    for part in psutil.disk_partitions():

        if "/media" in part.mountpoint or "/run/media" in part.mountpoint:
            print("clé déjà montée :", part.mountpoint)
            return part.device, part.mountpoint

    return None, None

def detect_usb_event(monitor):

    device = monitor.poll(timeout=0)

    if not device:
        return None

    print("event:", device.action, device.device_node, device.device_type)

    if device.action != "add":
        return None

    if device.device_type != "partition":
        return None

    if device.get("ID_BUS") != "usb":
        return None

    return device.device_node

import time

def wait_for_mount(device):

    for _ in range(20):  # 10 secondes max

        for part in psutil.disk_partitions():

            if part.device == device:
                print("clé montée :", part.mountpoint)
                return part.mountpoint

        time.sleep(0.5)

    return None

def copy_photos_to_usb(photo_path:str, usb_mount:str):
    dest = os.path.join(usb_mount, f"photomaton_{date.today()}")

    os.makedirs(dest, exist_ok=True)

    if os.path.isfile(photo_path):
        shutil.copy(photo_path, dest)
    print("photos copiées sur la clès USB")



