import subprocess
import sys

def check_printers() -> bool:
    """
    Vérifie si au moins une imprimante est configurée et accepte les travaux via CUPS.
    Retourne True si une imprimante est trouvée, False sinon.
    """
    if sys.platform not in ["linux", "darwin"]:
        # Sur les autres systèmes, on ne peut pas vérifier facilement, on suppose que c'est bon.
        return True
    try:
        # 'lpstat -a' liste les imprimantes qui acceptent des travaux,
        # mais 'lpstat -p' est plus fiable pour voir si une imprimante est simplement connectée et prête ('idle').
        result = subprocess.run(["lpstat", "-p"], check=True, capture_output=True, text=True)
        
        printers_found: list[str] = []
        for line in result.stdout.strip().split('\n'):
            # La ligne est du type "printer Canon_SELPHY_CP1300 is idle.  enabled since..."
            if "is idle" in line:
                parts: list[str] = line.split()
                if len(parts) > 1 and parts[0] == 'printer':
                    printer_name = parts[1]
                    printers_found.append(printer_name)
                    print(f"Imprimante détectée et prête : {printer_name}")

        return len(printers_found) > 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Gère le cas où 'lpstat' n'est pas trouvé ou retourne une erreur.
        print("Erreur lors de la vérification des imprimantes. CUPS est-il installé et en cours d'exécution ?")
        return False

def print_image(image_path: str, printer_name: str | None = None, printing_options: dict[str, str] | None = None) -> bool:
    """
    Envoie une image à l'imprimante via la ligne de commande 'lp'.
    Cette méthode est principalement compatible avec Linux et macOS (CUPS).
    Pour Windows, il faudrait utiliser une autre méthode (ex: via une librairie comme win32print).
    """
    if sys.platform not in ["linux", "darwin"]:
        print("L'impression automatique n'est supportée que sur Linux et macOS.")
        return False

    try:
        command: list[str] = ["lp"]
        if printer_name:
            # Ajoute l'option pour spécifier une imprimante
            command.extend(["-d", printer_name])
        
        # Ajoute les options d'impression supplémentaires si elles sont fournies
        if printing_options:
            for key, value in printing_options.items():
                command.extend(["-o", f"{key}={value}"])

        command.append(image_path)
        
        print(f"Exécution de la commande d'impression: {' '.join(command)}")
        subprocess.run(command, check=True)
        return True
    except FileNotFoundError:
        print("Erreur: La commande 'lp' n'a pas été trouvée. Assurez-vous que CUPS est installé et configuré.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'envoi à l'imprimante: {e}")
        return False