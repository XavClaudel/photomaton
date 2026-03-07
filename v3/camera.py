import subprocess
import os
from datetime import datetime

def capture_photo(tmp_dir):
    filename = datetime.now().strftime("capt_%Y_%m_%d-%H_%M_%S.jpg")
    path = os.path.join(tmp_dir, filename)

    try:
        subprocess.run([
            "gphoto2",
            "--capture-image-and-download",
            "--filename",
            path
        ], check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError("Erreur capture photo")

    return path