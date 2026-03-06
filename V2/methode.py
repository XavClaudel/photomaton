import datetime
import os
import subprocess


def take_photo(PHOTO_DIR):
    """Simule la prise d'une photo avec la webcam."""
    filename = f"photo_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    filepath = os.path.join(PHOTO_DIR, filename)
    print(f"filepath : {filepath}")
    print(f"pwd : {os.system("pwd")}")
    os.system(f"gphoto2 --capture-image-and-download --filename {os.environ.get('HOME')}/Documents/tmp/capt_%y_%m_%d-%H_%M_%S.jpg")

    return filepath

def print_document(file_path):
    """Simule l'impression d'un fichier."""
    # Exemple avec commande lpr sous Linux :
    # subprocess.run(["lpr", file_path])

    # Simulation
    return f"Fichier {file_path} envoyé à l'impression."

def create_hotspot(ssid, password):
    # Créer un hotspot Wi-Fi
    wifi_interface =get_wifi_interface_linux()[0]
    try:
        # Créer un nouveau point d'accès
        subprocess.run([
            'nmcli', 'device', 'wifi', 'hotspot',
            'ifname', f'{wifi_interface}', 'con-name', ssid,
            'ssid', ssid, 'band', 'bg', 'password', password
        ], check=True)
        print(f'Hotspot "{ssid}" créé avec succès.')
    except subprocess.CalledProcessError as e:
        print(f'Erreur lors de la création du hotspot : {e}')


def get_wifi_interface_linux():
    try:
        output = subprocess.check_output("iw dev | grep Interface", shell=True, text=True)
        interfaces = [line.split()[1] for line in output.strip().split("\n")]
        return interfaces
    except subprocess.CalledProcessError:
        return []

