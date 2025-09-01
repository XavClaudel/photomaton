import os
import time
import pygame
import sys
import pyudev
import subprocess
import qrcode
import RPi.GPIO as GPIO, time
import cups
from PIL import Image
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import gphoto2 as gp



# déclaration des ports GPIO que l'on utilise
GPIO.setmode(GPIO.BCM)
BUTTON_PIN_2 = 2
GPIO.setup(BUTTON_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialisation de Pygame
pygame.init()

# Définition des dimensions de la fenêtre
i = pygame.display.Info()
width = i.current_w
height = i.current_h
screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("PHOTOMATON")

# Définition des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Polices
font_large = pygame.font.Font(None, 120)
font_small = pygame.font.Font(None, 50)
font = pygame.font.Font(None, 74)


# Variables d'environnement
env_vars = ["PRINT", "DOWNLOAD", "CLES_USB", "RETOUR_IMAGE"]

# États initiaux des boutons glissants
toggles = [os.getenv(var) == "TRUE" for var in env_vars]

PORT = 8000
IMAGE_PATH = ""


class ImageHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path :
            print("here")
            try:
                with open(self.path, 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(404, f"File Not Found x:{IMAGE_PATH}")
        else:
            self.send_error(404, f"Not Found :{self.path}")

def draw_settings_screen(screen: pygame, toggles: list):
    screen.fill(BLACK)
    params = ["PRINT", "DOWNLOAD", "CLES_USB", "RETOUR_IMAGE"]
    for i, param in enumerate(params):
        text = font_small.render(param, 1, WHITE)
        screen.blit(text, (100, 100 + i * 100))
        draw_toggle_switch(
            screen=screen, position=(450, 100 + i * 100), state=toggles[i]
        )
    pygame.display.flip()


def draw_toggle_switch(screen: pygame, position: tuple, state: list):
    pygame.draw.rect(screen, WHITE, (*position, 60, 30), border_radius=15)
    if state:
        pygame.draw.circle(screen, GREEN, (position[0] + 45, position[1] + 15), 15)
    else:
        pygame.draw.circle(screen, RED, (position[0] + 15, position[1] + 15), 15)


def set_environment_variable(index: int, state: list):
    os.environ[env_vars[index]] = "TRUE" if state else "FALSE"


def draw_welcome_screen(screen: pygame, DECLENCHEUR: bool):
   

    screen.fill(BLACK)
    text = font_large.render("Bienvenue", 1, WHITE)
    text1 = font_small.render("Appuyer sur le déclencheur", 1, WHITE)
    text2 = font_small.render("pour prendre une photo", 1, WHITE)
    screen.blit(text, (300, 100))
    screen.blit(text1, (300, 300))
    screen.blit(text2, (300, 350))

    pygame.display.flip()


def timer(screen: pygame):
    for i in range(5, 0, -1):
        decompte = pygame.image.load(f"images/{i}.jpg").convert()
        screen.blit(pygame.transform.scale(decompte, (width, height)), (0, 0))
        pygame.display.flip()
        time.sleep(1)
    decompte = pygame.image.load("images/0.jpg").convert()
    screen.blit(pygame.transform.scale(decompte, (width, height)), (0, 0))
    pygame.display.flip()


def affichage(path: str, screen: pygame, width, height):
    # affichage de l'image
    screen.fill(BLACK)
    affichage = pygame.image.load(path).convert()
    screen.blit(pygame.transform.scale(affichage, (width, height)), (0, 0))
    pygame.display.flip()


def mount_usb(device_node: str, mount_point: str):
    try:
        os.makedirs(mount_point, exist_ok=True)
        subprocess.run(["mount", device_node, mount_point], check=True)
        print(f"Monté {device_node} sur {mount_point}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du montage de {device_node}: {e}")
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")


def monitor_usb(home: str) -> str:
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="block", device_type="partition")

    print("Surveillance des périphériques USB en cours...")

    for device in iter(monitor.poll, None):
        if device.action == "add":
            device_node = device.device_node
            mount_point = f"{home}/Documents/cles_usb_photos"
            if not os.path.exists(mount_point):  # Vérifier si le dossier n'existe pas
                os.makedirs(mount_point)  # Créer le dossier
            print(f"Nouvelle partition détectée : {device_node}")
            print(f"mount :{mount_point}")
            os.system(f"pmount {device_node} ")
            return device_node


def init():
    os.environ.get("PRINT", False)
    os.environ.get("DOWNLOAD", False)
    os.environ.get("CLES_USB", False)
    os.environ.get("RETOUR_IMAGE", False)
    creationdossier("Documents/photos")


def creationdossier(sous_chemin: str):
    home_dir = os.getenv("HOME")  # Récupérer la variable d'environnement HOME
    if home_dir is None:
        raise EnvironmentError("La variable d'environnement HOME n'est pas définie.")

    dir_path = os.path.join(home_dir, sous_chemin)  # Chemin complet du dossier

    if not os.path.exists(dir_path):  # Vérifier si le dossier n'existe pas
        os.makedirs(dir_path)  # Créer le dossier
        print(f"Le dossier '{dir_path}' a été créé.")
    else:
        print(f"Le dossier '{dir_path}' existe déjà.")


def creationdossier_usb(device_node: str, field: str) -> str:
    home_dir = f"/media/{device_node.split('/')[2]}/{field}"  # Récupérer la variable d'environnement HOME
    if home_dir is None:
        raise EnvironmentError("La variable d'environnement HOME n'est pas définie.")

    if not os.path.exists(home_dir):  # Vérifier si le dossier n'existe pas
        os.makedirs(home_dir)  # Créer le dossier
        print(f"Le dossier '{home_dir}' a été créé.")
    else:
        print(f"Le dossier '{home_dir}' existe déjà.")

    return home_dir


def draw_print_choice_screen(path: str, screen: pygame):
    lines = [
        "Voulez-vous imprimez",
        "cette photo ?",
        "",
        "Si oui, appuyer sur le déclencheur.",
        "",
        "Si non, attendez.",
    ]
    screen.fill(BLACK)
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (180, 150 + i * 50))

    pygame.display.flip()


def draw_print_screen(screen: pygame):
    screen.fill(BLACK)
    text = font.render("Impression", True, WHITE)
    screen.blit(text, (350, 250))
    pygame.display.flip()


def print_picture(path):
    conn = cups.Connection()

    # Obtenir l'imprimante par défaut
    printers = conn.getPrinters()
    printer_name = list(printers.keys())[0]  # Utilise la première imprimante trouvée
    print(f"printer name :{printer_name}")
    # Vérifier si le fichier image existe
    if not os.path.exists(path):
        raise FileNotFoundError(f"Le fichier {path} n'existe pas.")

    # Envoyer le fichier à l'imprimante
    os.system(f"lp -d {printer_name} {path}")

def capture_liveview_frame():
    context = gp.Context()
    camera = gp.Camera()
    camera.init(context)

    # Capture d'une image LiveView en utilisant libgphoto2
    camera_file = camera.capture_preview()
    file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
    return file_data
def display_liveview(DECLENCHEUR):
    # Initialiser libgphoto2 et l'appareil photo
    frame_data = capture_liveview_frame()

    # Charger l'image capturée en tant que surface Pygame
    image_surface = pygame.image.load(frame_data, 'jpg')
    image_surface = pygame.transform.scale(image_surface, (width, height))

    # Effacer l'écran et afficher l'image capturée
    screen.fill(BLACK)
    screen.blit(image_surface, (0, 0))
        
    # Mettre à jour l'affichage
    pygame.display.flip()
# Fonction pour lancer le serveur
def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, ImageHTTPRequestHandler)
    print(f"Starting server on port {PORT}...")
    httpd.serve_forever()


# Fonction pour générer un QR code à partir d'une URL
def generer_qr_code(url: str, nom_fichier: str = "qr_code.png") -> str:
    # Générer le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Créer l'image du QR code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Définir le chemin complet du fichier
    chemin_fichier = os.path.join(os.getcwd(), nom_fichier)
    
    # Enregistrer le QR code dans le dossier courant
    img.save(chemin_fichier)
    
    return chemin_fichier

def get_ip_address(interface):
    try:
        # Exécuter nmcli pour obtenir les informations de l'interface réseau
        result = subprocess.run(
            ['nmcli', '-g', 'IP4.ADDRESS', 'device', 'show', interface],
            capture_output=True, text=True, check=True
        )
        # Nettoyer le résultat
        ip_address = result.stdout.strip()
        if ip_address:
            print(f'Adresse IP assignée à {interface} : {ip_address}')
            return ip_address
        else:
            print(f'Aucune adresse IP trouvée pour l\'interface {interface}.')
    except subprocess.CalledProcessError as e:
        print(f'Erreur lors de l\'obtention de l\'adresse IP : {e}')
    except Exception as e:
        return f"Erreur lors de la récupération de l'IP réseau: {e}"
def create_hotspot(ssid, password):
    # Créer un hotspot Wi-Fi
    try:
        # Créer un nouveau point d'accès
        subprocess.run([
            'nmcli', 'device', 'wifi', 'hotspot',
            'ifname', 'wlan0', 'con-name', ssid,
            'ssid', ssid, 'band', 'bg', 'password', password
        ], check=True)
        print(f'Hotspot "{ssid}" créé avec succès.')
    except subprocess.CalledProcessError as e:
        print(f'Erreur lors de la création du hotspot : {e}')

def main():
    init()
    create_hotspot('photomaton', 'photomaton')
    running = True
    in_welcome_screen = False
    config_usb = True
    DECLENCHEUR = False
    home = f"{os.environ.get('HOME')}/Documents"
    os.system(f" rm -r {home}/tmp")
    creationdossier("Documents/tmp")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    in_welcome_screen = not in_welcome_screen
                    DECLENCHEUR = True
                if event.key == pygame.K_q:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not in_welcome_screen:
                for i in range(len(toggles)):
                    toggle_rect = pygame.Rect(450, 100 + i * 100, 60, 30)
                    if toggle_rect.collidepoint(event.pos):
                        toggles[i] = not toggles[i]
                        set_environment_variable(i, toggles[i])

        if in_welcome_screen:
            if os.environ.get("RETOUR_IMAGE"):
                display_liveview(DECLENCHEUR=DECLENCHEUR)
            else:
                draw_welcome_screen(screen=screen, DECLENCHEUR=DECLENCHEUR)

            if GPIO.input(BUTTON_PIN_2) == GPIO.LOW and DECLENCHEUR:
                DECLENCHEUR = False

                if os.environ.get("CLES_USB") and config_usb:
                    device_node = monitor_usb(home)
                    path_usb = creationdossier_usb(
                        device_node, field="photos"
                    )

                    config_usb = False
                timer(screen=screen)
                os.system(
                    f"gphoto2 --capture-image-and-download --filename {os.environ.get('HOME')}/Documents/tmp/capt_%y_%m_%d-%H_%M_%S.jpg"
                )

                os.system(f"cp {home}/tmp/*jpg {home}/photos")
                if os.environ.get("CLES_USB"):
                    os.system(f"cp {home}/tmp/*jpg {path_usb}")

                path = f"{home}/tmp/{os.listdir(f'{home}/tmp/')[0]}"
                affichage(path=path, screen=screen, width=width, height=height)
                time.sleep(8)
                DECLENCHEUR = True
                if os.environ.get("PRINT"):
                    while True:
                        button_pressed = False
                        draw_print_choice_screen(path=path, screen=screen)
                        start_time = time.time()
                        while time.time() - start_time < 10:
                            if GPIO.input(BUTTON_PIN_2) == GPIO.LOW:
                                button_pressed = True
                                draw_print_screen(screen=screen)
                                print_picture(path=path)
                                time.sleep(65)

                                break
                        if not button_pressed:
                            break

                if os.environ.get("DOWNLOAD"):
                    if not os.path.exists("/tmp/photomaton"):
                        os.system("mkdir /tmp/photomaton")
                    os.system(f"cp {home}/tmp/*jpg /tmp/photomaton")
                   
                    # Chemin de l'image locale
                    
                    image_path = f'/tmp/photomaton/{path.split("/")[-1]}'  # Remplace par le chemin de ton image
                    ip = get_ip_address('wlan0').split('/')[0]
                    print(f"ip :{ip}")
                    # Générer une URL pour l'image (simuler une URL locale)
                    url = f"http://{ip}:8000{image_path}"
                    print(f"url : {url}")
                    # Générer le QR code avec l'URL
                    qr_code_path = generer_qr_code(url)
                    os.system(" cd /tmp/photomaton")
                    server_thread = threading.Thread(target=run_server)
                    server_thread.daemon = True  # Le thread se termine lorsque le programme principal se termine
                    server_thread.start()
                    print("Le serveur fonctionne en arrière-plan.")
                    # Afficher le QR code dans une fenêtre pygame
                    RUN_AFFICHAGE = True
                    while RUN_AFFICHAGE:
                        
                        affichage(
                        path=qr_code_path, screen=screen, width=500, height=500
                    )
                        start_time = time.time()
                        while time.time() - start_time < 20:
                            RUN_AFFICHAGE = False
                        if  os.path.exists(f"{qr_code_path}"):      
                            os.system(f" rm {qr_code_path}")
                    os.system(" rm /tmp/photomaton/*jpg")
                os.system(f" rm {home}/tmp/*jpg")
                if os.environ.get("RETOUR_IMAGE"):
                    display_liveview(DECLENCHEUR=DECLENCHEUR)
                else:
                    draw_welcome_screen(screen=screen, DECLENCHEUR=DECLENCHEUR)
        else:
            draw_settings_screen(screen=screen, toggles=toggles)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
