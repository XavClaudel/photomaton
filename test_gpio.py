"""Test du bouton GPIO, en dehors de l'application. Usage : .venv/bin/python test_gpio.py [broche]"""
import sys
import traceback

pin = int(sys.argv[1]) if len(sys.argv) > 1 else 2
print(f"Python : {sys.executable}")

try:
    import gpiozero
    from gpiozero import Button, Device
    print(f"gpiozero {gpiozero.__version__} importé.")
    button = Button(pin, pull_up=True, bounce_time=0.1)
    print(f"Pin factory : {type(Device.pin_factory).__name__}")
    print(f"OK : bouton configuré sur GPIO{pin}. Appuie sur le bouton (Ctrl+C pour quitter)...")
    button.when_pressed = lambda: print("  -> appui détecté !")
    from signal import pause
    pause()
except KeyboardInterrupt:
    print("Fin du test.")
except Exception:
    print(f"ÉCHEC sur GPIO{pin} :")
    traceback.print_exc()
