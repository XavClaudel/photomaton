import json
import os
from typing import Any

CONFIG_FILE: str = 'config.json'

# Configuration par défaut utilisée si le fichier n'existe pas ou est corrompu.
DEFAULT_CONFIG: dict[str, Any] = {
    "countdown_seconds": 5,
    "max_prints_per_photo": 2,
    "printer_name": None,
    "print_fit_method": "pad", # 'pad' (bandes noires) ou 'crop' (rogner)
    "printing_options": {
        "media": "Postcard",
        "print-quality": "5",
        "StpBorderless": "True"
    },
    "enable_printing": True,
    "enable_usb_save": True,
    "enable_web_server": True,
    "web_server_ip": None, # Forcer une IP pour le QR Code (utile en mode Point d'Accès)
    "hotspot_ssid": "photomaton",
    "hotspot_password": "photobooth",
    "enable_personalization": True,
    "overlay_path": "assets/overlay.png",
    "enable_text_marking": False,
    "marking_text": "Mon Super Evénement",
    "marking_text_color": "Blanc",
    "marking_text_position": "En bas à droite",
    "marking_text_font": "Lobster-Regular.ttf",
    "marking_text_size": 60,
    "gpio_button_pin": 2, # Pin BCM pour le bouton physique
}

def load_config() -> dict[str, Any]:
    """Charge la configuration depuis config.json. Crée le fichier s'il n'existe pas."""
    if not os.path.exists(CONFIG_FILE):
        print("Fichier de configuration non trouvé. Création d'un nouveau avec les valeurs par défaut.")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config: dict[str, Any] = json.load(f)
            # On s'assure que toutes les clés par défaut sont présentes dans le fichier chargé
            config = {**DEFAULT_CONFIG, **config}
            return config
    except (json.JSONDecodeError):
        print("Fichier de configuration invalide. Utilisation des valeurs par défaut.")
        return DEFAULT_CONFIG

def save_config(config_data: dict[str, Any]) -> None:
    """Sauvegarde le dictionnaire de configuration dans config.json."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)