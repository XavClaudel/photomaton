import os

HOME = os.getenv("HOME")
PWD = os.getenv("PWD")
PHOTO_DIR = f"{PWD}/photo"
TMP_DIR = f"{PWD}/tmp_test"

PARAMS = {
    "CLES_USB": {
        "label": "Copie sur clé USB",
        "value": True
    },
    "IMPRIMER": {
        "label": "Imprimer la photo",
        "value": False
    },
    "QR_CODE": {

        "label": "QR Code",
        "value": False
    }
}


BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,200,0)
RED = (200,0,0)
GRAY = (180,180,180)
DARK_GRAY = (50,50,50)

WIDTH = 800 
HEIGHT = 480


# PORT = 8000

# HOTSPOT_SSID = "photomaton"
# HOTSPOT_PASSWORD = "photomaton"

# BUTTON_PIN = 2

# COUNTDOWN = 5
# DISPLAY_TIME = 8
# PRINT_TIMEOUT = 10