import cv2
import time
import os
import numpy as np
import subprocess
import shutil

# Variable globale pour la capture vidéo, accessible par toutes les fonctions du module.
cap: cv2.VideoCapture | None = None
# Variable globale pour savoir si un appareil reflex est connecté et utilisable
IS_DSLR_CONNECTED: bool = False
# Variable globale pour savoir si une webcam est disponible
IS_WEBCAM_AVAILABLE: bool = False

def free_usb_device():
    """Tente de tuer les processus gvfs qui bloquent l'accès à la caméra USB."""
    try:
        subprocess.run(["pkill", "-f", "gvfs-gphoto2-volume-monitor"], capture_output=True)
        subprocess.run(["pkill", "-f", "gvfsd-gphoto2"], capture_output=True)
    except Exception as e:
        pass

def check_dslr() -> bool:
    """Vérifie si gphoto2 est installé et si une caméra est détectée."""
    free_usb_device()
    if not shutil.which("gphoto2"):
        print("INFO: 'gphoto2' n'est pas installé. Le support pour appareil reflex est désactivé.")
        return False
    
    try:
        # Exécute 'gphoto2 --auto-detect' pour voir si une caméra est listée.
        result = subprocess.run(["gphoto2", "--auto-detect"], capture_output=True, text=True, timeout=10)
        # On vérifie que la sortie contient plus que les lignes d'en-tête
        lines = result.stdout.strip().split('\n')
        if len(lines) > 2: # "Model", "Port", "----------------", "Camera Name..."
            print(f"INFO: Appareil photo reflex (DSLR) détecté via gphoto2:\n{result.stdout.strip()}")
            return True
        else:
            print("INFO: gphoto2 est installé, mais aucun appareil photo reflex n'a été détecté.")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"INFO: Erreur lors de la détection du DSLR avec gphoto2: {e}")
        return False

def init_camera(camera_index: int = 0) -> bool:
    """
    Initialise les caméras. Vérifie le reflex (DSLR) et la webcam.
    Retourne True si au moins un des deux est disponible.
    """
    global cap, IS_DSLR_CONNECTED, IS_WEBCAM_AVAILABLE
    
    # 1. Vérifier la présence d'un appareil reflex (DSLR)
    IS_DSLR_CONNECTED = check_dslr()

    # 2. Initialiser la webcam pour le retour vidéo (live preview)
    cap = cv2.VideoCapture(camera_index)
    if cap.isOpened():
        IS_WEBCAM_AVAILABLE = True
        # Configure la résolution de la caméra pour une meilleure qualité.
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        print(f"INFO: Webcam initialisée pour le retour vidéo (index {camera_index}).")
    else:
        IS_WEBCAM_AVAILABLE = False
        print(f"INFO: Aucune webcam trouvée à l'index {camera_index}.")
        
    if IS_DSLR_CONNECTED:
        print("INFO: L'appareil reflex sera utilisé pour la capture finale en haute qualité.")
    
    if not IS_WEBCAM_AVAILABLE and not IS_DSLR_CONNECTED:
        print("ERREUR: Aucune webcam ni appareil reflex n'a été détecté. Impossible de continuer.")
        return False
    elif not IS_DSLR_CONNECTED:
        print("INFO: La webcam sera utilisée pour la capture finale.")
        
    return True

def get_frame() -> np.ndarray | None:
    """Capture une seule image (frame) depuis le flux de la WEBCAM pour le retour vidéo."""
    if IS_WEBCAM_AVAILABLE and cap and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            # OpenCV lit les images en format BGR (Bleu, Vert, Rouge).
            # On le convertit en RGB (Rouge, Vert, Bleu) pour une compatibilité
            # avec Pillow et Tkinter.
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return None

def take_picture(save_folder: str = 'photos') -> str | None:
    """
    Prend une photo. Utilise l'appareil reflex (DSLR) si disponible, sinon la webcam.
    Retourne le chemin du fichier sauvegardé.
    """
    if IS_DSLR_CONNECTED:
        return take_picture_with_dslr(save_folder)
    elif IS_WEBCAM_AVAILABLE:
        return take_picture_with_webcam(save_folder)
    else:
        print("ERREUR: Aucune caméra disponible pour prendre une photo.")
        return None

def take_picture_with_dslr(save_folder: str) -> str | None:
    """Prend une photo avec l'appareil reflex via gphoto2."""
    print("Déclenchement de la capture avec l'appareil reflex...")
    free_usb_device()
    try:
        timestamp: str = time.strftime("%Y%m%d-%H%M%S")
        filename: str = f"photomaton_dslr_{timestamp}.jpg"
        filepath = os.path.join(save_folder, filename)
        
        command = ["gphoto2", "--capture-image-and-download", "--filename", filepath]
        subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
        
        if os.path.exists(filepath):
            print(f"Photo (reflex) sauvegardée : {filepath}")
            return filepath
        else:
            print("Erreur: gphoto2 a terminé sans erreur mais le fichier est introuvable.")
            return None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Erreur lors de la capture avec gphoto2: {e}\nSortie d'erreur:\n{e.stderr}")
        return None

def take_picture_with_webcam(save_folder: str = 'photos') -> str | None:
    """Prend une photo avec la webcam, la sauvegarde et retourne son chemin."""
    frame = get_frame()
    if frame is not None:
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Reconvertir en BGR pour la sauvegarde
        try:
            timestamp: str = time.strftime("%Y%m%d-%H%M%S")
            filename: str = f"photomaton_webcam_{timestamp}.jpg"
            filepath = os.path.join(save_folder, filename)
            cv2.imwrite(filepath, frame_bgr)
            print(f"Photo (webcam) sauvegardée : {filepath}")
            return filepath
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'image : {e}")
            return None
    return None

def release_camera() -> None:
    """Libère la ressource de la webcam proprement à la fin du programme."""
    global IS_WEBCAM_AVAILABLE
    if cap:
        cap.release()
        print("Webcam libérée.")
    IS_WEBCAM_AVAILABLE = False