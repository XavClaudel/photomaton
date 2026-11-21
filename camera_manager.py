import cv2
import time
import os
import numpy as np
import subprocess
import shutil
import threading
import signal

# Variable globale pour la capture vidéo, accessible par toutes les fonctions du module.
cap: cv2.VideoCapture | None = None
# Variable globale pour le processus gphoto2 en mode capture movie (live view)
dslr_process: subprocess.Popen | None = None
# Variable globale pour savoir si un appareil reflex est connecté et utilisable
IS_DSLR_CONNECTED: bool = False
# Variable globale pour savoir si une webcam est disponible
IS_WEBCAM_AVAILABLE: bool = False
# Source actuelle du live view, détectée automatiquement ('webcam' ou 'dslr')
LIVE_VIEW_SOURCE: str = 'webcam'
# Thread de lecture du flux live view DSLR et dernière image décodée
_dslr_reader_thread: threading.Thread | None = None
_dslr_latest_frame: np.ndarray | None = None
_dslr_frame_lock = threading.Lock()

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

def init_camera(camera_index: int = 0, start_live_view: bool = True) -> bool:
    """
    Initialise les caméras avec détection automatique de la source du retour vidéo :
    - si un reflex est détecté et que son live view fonctionne, il est utilisé ;
    - sinon, repli sur la webcam.
    Le reflex (s'il est présent) reste utilisé pour la capture finale dans tous les cas.

    Si start_live_view est False, on se contente de détecter le matériel (sans laisser
    tourner le live view du reflex), par exemple au démarrage pendant l'écran de configuration.
    Retourne True si au moins un des deux est disponible.
    """
    global cap, IS_DSLR_CONNECTED, IS_WEBCAM_AVAILABLE, LIVE_VIEW_SOURCE

    # 0. Libérer les ressources d'une éventuelle initialisation précédente
    stop_dslr_live_view()
    if cap is not None:
        cap.release()
        cap = None
    IS_WEBCAM_AVAILABLE = False
    LIVE_VIEW_SOURCE = 'webcam'

    # 1. Vérifier la présence d'un appareil reflex (DSLR)
    IS_DSLR_CONNECTED = check_dslr()

    # 2. Si un reflex est présent, on tente son live view en priorité
    if IS_DSLR_CONNECTED and start_live_view:
        if start_dslr_live_view():
            LIVE_VIEW_SOURCE = 'dslr'
            print("INFO: Retour vidéo assuré par le live view du reflex.")
        else:
            print("INFO: Live view du reflex indisponible, repli sur la webcam pour le retour vidéo.")

    # 3. Sinon, webcam pour le retour vidéo
    if LIVE_VIEW_SOURCE == 'webcam':
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            IS_WEBCAM_AVAILABLE = True
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            print(f"INFO: Webcam initialisée pour le retour vidéo (index {camera_index}).")
        else:
            cap.release()
            cap = None
            print(f"INFO: Aucune webcam trouvée à l'index {camera_index}.")

    if IS_DSLR_CONNECTED:
        print("INFO: L'appareil reflex sera utilisé pour la capture finale en haute qualité.")

    if not IS_WEBCAM_AVAILABLE and not IS_DSLR_CONNECTED:
        print("ERREUR: Aucune webcam ni appareil reflex n'a été détecté. Impossible de continuer.")
        return False
    elif not IS_DSLR_CONNECTED:
        print("INFO: La webcam sera utilisée pour la capture finale.")

    return True

def start_dslr_live_view() -> bool:
    """
    Démarre le live view du reflex : gphoto2 envoie un flux MJPEG sur stdout,
    un thread de fond le lit en continu et ne conserve que la dernière image.
    """
    global dslr_process, _dslr_reader_thread, _dslr_latest_frame
    stop_dslr_live_view()
    free_usb_device()
    try:
        cmd = ["gphoto2", "--capture-movie", "--stdout"]
        dslr_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
    except Exception as e:
        print(f"Erreur lors du démarrage du Live View DSLR: {e}")
        dslr_process = None
        return False

    with _dslr_frame_lock:
        _dslr_latest_frame = None
    _dslr_reader_thread = threading.Thread(target=_dslr_reader_loop, args=(dslr_process,), daemon=True)
    _dslr_reader_thread.start()

    # On attend la première image pour valider que le live view fonctionne réellement.
    deadline = time.time() + 5
    while time.time() < deadline:
        with _dslr_frame_lock:
            if _dslr_latest_frame is not None:
                return True
        if dslr_process.poll() is not None:
            break
        time.sleep(0.05)
    print("ERREUR: Le reflex n'a envoyé aucune image de live view.")
    stop_dslr_live_view()
    return False

def _dslr_reader_loop(process: subprocess.Popen) -> None:
    """Thread de fond : découpe le flux MJPEG en images JPEG et décode la plus récente."""
    global _dslr_latest_frame
    buffer = bytearray()
    stream = process.stdout
    while process.poll() is None:
        try:
            chunk = stream.read(65536)
        except Exception:
            break
        if not chunk:
            break
        buffer += chunk

        # Extrait la dernière image JPEG complète du buffer (on ignore les plus anciennes
        # pour ne jamais accumuler de retard).
        last_jpeg = None
        while True:
            start = buffer.find(b'\xff\xd8')
            if start == -1:
                # Pas de début d'image : on ne garde qu'un octet au cas où 0xFF serait coupé
                del buffer[:-1]
                break
            end = buffer.find(b'\xff\xd9', start + 2)
            if end == -1:
                del buffer[:start]
                break
            last_jpeg = bytes(buffer[start:end + 2])
            del buffer[:end + 2]

        if last_jpeg is not None:
            frame = cv2.imdecode(np.frombuffer(last_jpeg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                with _dslr_frame_lock:
                    _dslr_latest_frame = rgb

        # Sécurité : évite une croissance infinie si le flux est corrompu
        if len(buffer) > 10 * 1024 * 1024:
            buffer.clear()

def stop_dslr_live_view():
    """Arrête le processus de live view DSLR s'il est en cours."""
    global dslr_process, _dslr_reader_thread, _dslr_latest_frame
    if dslr_process:
        # SIGINT permet à gphoto2 de refermer proprement le miroir/viewfinder
        try:
            dslr_process.send_signal(signal.SIGINT)
            dslr_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            dslr_process.kill()
            dslr_process.wait()
        except Exception:
            pass
        dslr_process = None
    if _dslr_reader_thread:
        _dslr_reader_thread.join(timeout=1)
        _dslr_reader_thread = None
    with _dslr_frame_lock:
        _dslr_latest_frame = None

def is_live_view_available() -> bool:
    """Indique si un retour vidéo (webcam ou reflex) est disponible."""
    if LIVE_VIEW_SOURCE == 'dslr':
        return dslr_process is not None and dslr_process.poll() is None
    return IS_WEBCAM_AVAILABLE

def get_frame() -> np.ndarray | None:
    """Capture une seule image (frame) depuis le flux sélectionné (WEBCAM ou DSLR)."""
    if LIVE_VIEW_SOURCE == 'webcam':
        if IS_WEBCAM_AVAILABLE and cap and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    elif LIVE_VIEW_SOURCE == 'dslr':
        return get_dslr_frame()
    return None

def get_dslr_frame() -> np.ndarray | None:
    """Retourne (sans bloquer) la dernière image reçue du live view reflex."""
    with _dslr_frame_lock:
        return _dslr_latest_frame

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
    
    # IMPORTANT: Si le live view est actif, il faut l'arrêter car il monopolise l'USB
    was_live_view_active = (LIVE_VIEW_SOURCE == 'dslr')
    if was_live_view_active:
        stop_dslr_live_view()
        time.sleep(1) # Laisser un peu de temps à la caméra pour changer de mode

    free_usb_device()
    filepath = None
    try:
        timestamp: str = time.strftime("%Y%m%d-%H%M%S")
        filename: str = f"photomaton_dslr_{timestamp}.jpg"
        filepath = os.path.join(save_folder, filename)
        
        command = ["gphoto2", "--capture-image-and-download", "--filename", filepath]
        subprocess.run(command, capture_output=True, text=True, check=True, timeout=30)
        
        if os.path.exists(filepath):
            print(f"Photo (reflex) sauvegardée : {filepath}")
        else:
            print("Erreur: gphoto2 a terminé sans erreur mais le fichier est introuvable.")
            filepath = None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Erreur lors de la capture avec gphoto2: {e}")
        if hasattr(e, 'stderr'):
            print(f"Sortie d'erreur:\n{e.stderr}")
        filepath = None
    
    # Redémarrer le live view si nécessaire
    if was_live_view_active:
        if not start_dslr_live_view():
            print("AVERTISSEMENT: Impossible de relancer le Live View DSLR après la capture.")
    
    return filepath

def take_picture_with_webcam(save_folder: str = 'photos') -> str | None:
    """Prend une photo avec la webcam, la sauvegarde et retourne son chemin."""
    # On utilise get_frame qui gère déjà la source
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
    """Libère toutes les ressources caméras proprement."""
    global IS_WEBCAM_AVAILABLE, cap
    stop_dslr_live_view()
    if cap:
        cap.release()
        print("Webcam libérée.")
    cap = None
    IS_WEBCAM_AVAILABLE = False