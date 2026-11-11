import psutil
import shutil
import os
import time

def find_usb_drive() -> str | None:
    """
    Tente de trouver le point de montage d'un lecteur USB.
    Cette méthode est une heuristique : elle cherche des disques 'removable'
    ou montés dans des chemins typiques comme '/media'.
    """
    for part in psutil.disk_partitions():
        if 'removable' in part.opts or '/media/' in part.mountpoint:
            print(f"Clé USB trouvée à : {part.mountpoint}")
            return part.mountpoint
    return None

def save_photo_to_usb(photo_path: str, usb_path: str) -> None:
    """
    Copie la photo vers un dossier 'Photomaton/[DATE_DU_JOUR]' sur la clé USB.
    """
    if not os.path.exists(usb_path):
        raise FileNotFoundError("Le chemin de la clé USB n'existe pas.")
    
    # Crée un sous-dossier avec la date du jour à l'intérieur du dossier 'Photomaton'
    today_str = time.strftime("%Y-%m-%d")
    save_dir = os.path.join(usb_path, "Photomaton", today_str)

    os.makedirs(save_dir, exist_ok=True) # Crée le dossier de la date s'il n'existe pas
    shutil.copy(photo_path, save_dir)
    print(f"Photo copiée vers {os.path.join(save_dir, os.path.basename(photo_path))}")