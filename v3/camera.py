import subprocess
from pathlib import Path
from datetime import datetime

def capture_image(tmp_dir):

    filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S.jpg")
    path = Path(tmp_dir) / filename

    cmd = [
        "gphoto2",
        "--capture-image-and-download",
        "--filename",
        str(path)
    ]

    subprocess.run(cmd, check=True)

    return path