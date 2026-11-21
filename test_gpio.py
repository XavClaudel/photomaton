"""
Diagnostic du bouton GPIO, en dehors de l'application.
Usage : .venv/bin/python test_gpio.py [broche]
"""
import glob
import os
import platform
import subprocess
import sys

pin = int(sys.argv[1]) if len(sys.argv) > 1 else 2


def run(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return (r.stdout + r.stderr).strip()
    except Exception as e:
        return f"(indisponible : {e})"


print("=== Système ===")
print(f"Python  : {sys.executable}")
try:
    print(f"Modèle  : {open('/proc/device-tree/model').read().strip(chr(0))}")
except Exception:
    print("Modèle  : inconnu")
print(f"Noyau   : {platform.release()}")
print(f"Puces   : {sorted(glob.glob('/dev/gpiochip*'))}")
print(f"gpiodetect :\n{run(['gpiodetect'])}")
print(f"État de la broche (pinctrl get {pin}) : {run(['pinctrl', 'get', str(pin)])}")
print(f"I2C actif : {'oui' if glob.glob('/dev/i2c-*') else 'non'} {sorted(glob.glob('/dev/i2c-*'))}")

print("\n=== Tests de réservation de la broche ===")
from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory

working = None
tests = [("par défaut", None)] + [(f"gpiochip{n}", n) for n in (0, 4)
                                    if os.path.exists(f"/dev/gpiochip{n}")]
for label, chip in tests:
    try:
        factory = LGPIOFactory() if chip is None else LGPIOFactory(chip=chip)
        button = Button(pin, pull_up=True, bounce_time=0.1, pin_factory=factory)
        print(f"[OK]    GPIO{pin} avec {label}")
        button.close()
        factory.close()
        working = working or (label, chip)
    except Exception as e:
        print(f"[ÉCHEC] GPIO{pin} avec {label} : {type(e).__name__}: {e}")

if working:
    label, chip = working
    print(f"\nGPIO{pin} fonctionne ({label}). Appuie sur le bouton (Ctrl+C pour quitter)...")
    factory = LGPIOFactory() if chip is None else LGPIOFactory(chip=chip)
    button = Button(pin, pull_up=True, bounce_time=0.1, pin_factory=factory)
    button.when_pressed = lambda: print("  -> appui détecté !")
    try:
        from signal import pause
        pause()
    except KeyboardInterrupt:
        print("Fin du test.")
else:
    print(f"\nAucune configuration ne permet d'utiliser GPIO{pin}. "
          f"Essaie une autre broche : .venv/bin/python test_gpio.py 17")
