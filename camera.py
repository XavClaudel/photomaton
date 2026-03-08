import subprocess
from pathlib import Path
from datetime import datetime


def take_picture(tmp_dir: str):

    filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S.jpg")
    path = Path(tmp_dir) / filename

    # libérer la caméra
    subprocess.run(["killall", "gvfs-gphoto2-volume-monitor"], stderr=subprocess.DEVNULL)
    subprocess.run(["killall", "gvfsd-gphoto2"], stderr=subprocess.DEVNULL)

    cmd = [
        "gphoto2",
        "--capture-image-and-download",
        "--force-overwrite",
        "--filename",
        str(path)
    ]

    subprocess.run(cmd, check=True)

    return path