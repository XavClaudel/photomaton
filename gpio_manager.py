import time
import os
from typing import Callable

# Variable pour savoir si on est sur un RPi
IS_RASPBERRY_PI: bool = os.path.exists('/proc/device-tree/model') and 'raspberry pi' in open('/proc/device-tree/model').read().lower()
GPIO_SETUP_SUCCESS: bool = False
button_device = None

# On importe la librairie GPIO uniquement si on est sur un RPi
if IS_RASPBERRY_PI:
    try:
        from gpiozero import Button
    except ImportError as e:
        print(f"Erreur: Impossible d'importer gpiozero. {e}")
        IS_RASPBERRY_PI = False # On force à False si l'import échoue
else:
    print("INFO: Pas un Raspberry Pi. Le module GPIO ne sera pas utilisé.")

def setup_button(pin: int, callback: Callable[[int], None]) -> None:
    """
    Configure un bouton sur une broche GPIO et attache une fonction de callback.
    """
    global GPIO_SETUP_SUCCESS, button_device
    if not IS_RASPBERRY_PI:
        return

    # Configure la broche en entrée avec une résistance de pull-up interne.
    # Le bouton doit être connecté entre la broche et la masse (GND).
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Un bounce_time trop élevé peut faire rater des appuis rapides
            button_device = Button(pin, bounce_time=0.1, pull_up=True)
            
        def on_press():
            print(f"[DEBUG GPIO] Appui physique détecté sur la broche {pin} par gpiozero !")
            callback(pin)

        button_device.when_pressed = on_press
        print(f"Bouton configuré sur la broche GPIO {pin} avec gpiozero. Prêt à déclencher la capture.")
        GPIO_SETUP_SUCCESS = True
    except Exception as e:
        print(f"Erreur d'accès aux GPIO (droits insuffisants ?): {e}. Le bouton physique GPIO est désactivé.")

def cleanup() -> None:
    """Nettoie les configurations GPIO à la fermeture."""
    global button_device
    if IS_RASPBERRY_PI and GPIO_SETUP_SUCCESS:
        print("Nettoyage des broches GPIO.")
        if button_device:
            button_device.close()