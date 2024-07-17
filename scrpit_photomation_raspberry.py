import os
import time
import pygame
import sys
import pyudev
import subprocess
import qrcode
from concurrent.futures import ThreadPoolExecutor
import RPi.GPIO as GPIO, time

#déclaration des ports GPIO que l'on utilise
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN )
GPIO.setup(3, GPIO.IN)

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 640, 480
fenetre = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

# Polices
font_large = pygame.font.Font(None, 120)
font_small = pygame.font.Font(None, 50)

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Variables d'environnement
env_vars = ["DROIT_A_L_IMAGE", "PRINT", "DOWNLOAD", "CLES_USB"]

# États initiaux des boutons glissants
toggles = [os.getenv(var) == "TRUE" for var in env_vars]


def draw_toggle_switch(screen, position, state):
    pygame.draw.rect(screen, WHITE, (*position, 60, 30), border_radius=15)
    if state:
        pygame.draw.circle(screen, GREEN, (position[0] + 45, position[1] + 15), 15)
    else:
        pygame.draw.circle(screen, RED, (position[0] + 15, position[1] + 15), 15)


def draw_settings_screen(screen, toggles):
    screen.fill(BLACK)
    params = ["DROIT_A_L_IMAGE", "PRINT", "DOWNLOAD", "CLES_USB"]
    for i, param in enumerate(params):
        text = font_small.render(param, 1, WHITE)
        screen.blit(text, (100, 100 + i * 100))
        draw_toggle_switch(screen, (450, 100 + i * 100), toggles[i])
    pygame.display.flip()


def draw_welcome_screen(screen):
    screen.fill(BLACK)
    text = font_large.render("Bienvenue", 1, WHITE)
    if os.environ.get("DROIT_A_L_IMAGE"):
        text1 = font_small.render("Appuyer sur le bouton vert", 1, (255, 255, 255))
        text2 = font_small.render(
            "pour céder votre droits à l'image", 1, (255, 255, 255)
        )
        text3 = font_small.render(
            "Sinon appuyer sur le bouton rouge", 1, (255, 255, 255)
        )
        screen.blit(text, (100, 0))
        screen.blit(text1, (15, 150))
        screen.blit(text2, (15, 200))
        screen.blit(text3, (15, 300))
    else:
        text1 = font_small.render("Appuyer sur le déclencheur", 1, (255, 255, 255))
        text2 = font_small.render("pour prendre une photo", 1, (255, 255, 255))
        screen.blit(text, (100, 0))
        screen.blit(text1, (15, 150))
        screen.blit(text2, (15, 200))

    pygame.display.flip()


def set_environment_variable(index, state):
    os.environ[env_vars[index]] = "TRUE" if state else "FALSE"


def timer():
    fenetre = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
    for i in range(5, -1, -1):
        decompte = pygame.image.load(f"images/{i}.jpg").convert()
        fenetre.blit(pygame.transform.scale(decompte, (640, 480)), (0, 0))
        pygame.display.flip()
        time.sleep(1)


def init():
    os.environ.get("DROIT_A_L_IMAGE", False)
    os.environ.get("PRINT", False)
    os.environ.get("DOWNLOAD", False)
    os.environ.get("CLES_USB", False)
    creationdossier("documents/photos/droit_a_l_image")
    creationdossier("documents/photos/pas_droit_a_l_image")
    creationdossier("documents/tmp")


def print_image():
    print("print")
    time.sleep(5)


def start_http_server(racine):
    os.system(f"cd {racine} && python3 -m http.server 9999")


def generate_qr_code(data="https://www.example.com", filename="qrcode.png"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save(filename)
    print(f"QR Code generated and saved as {filename}")


def download(home, path):
    if os.environ.get("DROIT_A_L_IMAGE"):
        racine = f"{home}/photos/droit_a_l_image"

    else:
        racine = f"{home}/photos/pas_droit_a_l_image"

    
    qr_data = "https://www.example.com"
    qr_filename = "qrcode.png"
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(start_http_server, racine),
            executor.submit(generate_qr_code, qr_data, qr_filename),
        ]

        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")


def creationdossier(sous_chemin):
    home_dir = os.getenv("HOME")  # Récupérer la variable d'environnement HOME
    if home_dir is None:
        raise EnvironmentError("La variable d'environnement HOME n'est pas définie.")

    dir_path = os.path.join(home_dir, sous_chemin)  # Chemin complet du dossier

    if not os.path.exists(dir_path):  # Vérifier si le dossier n'existe pas
        os.makedirs(dir_path)  # Créer le dossier
        print(f"Le dossier '{dir_path}' a été créé.")
    else:
        print(f"Le dossier '{dir_path}' existe déjà.")


def creationdossier_usb(device_node, field):
    home_dir = f"/media/{device_node.split('/')[2]}/{field}"  # Récupérer la variable d'environnement HOME
    if home_dir is None:
        raise EnvironmentError("La variable d'environnement HOME n'est pas définie.")

    if not os.path.exists(home_dir):  # Vérifier si le dossier n'existe pas
        os.makedirs(home_dir)  # Créer le dossier
        print(f"Le dossier '{home_dir}' a été créé.")
    else:
        print(f"Le dossier '{home_dir}' existe déjà.")

    return home_dir


def affichage(path):
    # affichage de l'image
    fenetre = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
    affichage = pygame.image.load(path).convert()
    fenetre.blit(pygame.transform.scale(affichage, (640, 480)), (0, 0))
    pygame.display.flip()
    time.sleep(5)


def montage_cles_usb():
    dir_path = f"/media/{os.environ.get('LOGNAME')}/PHOTOS"
    if not os.path.exists(dir_path):  # Vérifier si le dossier n'existe pas
        os.makedirs(dir_path)  # Créer le dossier
    os.system(f"mount /dev/sdc1 {dir_path}")


def mount_usb(device_node, mount_point):
    """
    Monte le périphérique USB.
    :param device_node: Le noeud de périphérique (par exemple, /dev/sdb1).
    :param mount_point: Le point de montage où monter le volume.
    """
    try:
        os.makedirs(mount_point, exist_ok=True)
        subprocess.run(["mount", device_node, mount_point], check=True)
        print(f"Monté {device_node} sur {mount_point}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du montage de {device_node}: {e}")
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")


def monitor_usb(home):
    """
    Surveille les événements de connexion de périphériques USB et monte les nouveaux volumes.
    """
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="block", device_type="partition")

    print("Surveillance des périphériques USB en cours...")

    for device in iter(monitor.poll, None):
        if device.action == "add":
            device_node = device.device_node
            mount_point = f"home/xav/documents/cles_usb_photos"
            if not os.path.exists(mount_point):  # Vérifier si le dossier n'existe pas
                os.makedirs(mount_point)  # Créer le dossier
            print(f"Nouvelle partition détectée : {device_node}")
            print(f"mount :{mount_point}")
            os.system(f"pmount {device_node} ")
            return device_node


def main():
    init()
    running = True
    in_welcome_screen = False
    config_usb = 1
    while running:
    etat=GPIO.input (2)
    print(etat)    
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z :
                    in_welcome_screen = not in_welcome_screen
            elif event.type == pygame.MOUSEBUTTONDOWN and not in_welcome_screen:
                for i in range(len(toggles)):
                    toggle_rect = pygame.Rect(450, 100 + i * 100, 60, 30)
                    if toggle_rect.collidepoint(event.pos):
                        toggles[i] = not toggles[i]
                        set_environment_variable(i, toggles[i])

        if in_welcome_screen:
            draw_welcome_screen(screen=fenetre)
            # print(os.environ)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        home = f"{os.environ.get('HOME')}/documents"
                        if os.environ.get("CLES_USB") and config_usb == 1:
                            print("cles_usb")
                            device_node = monitor_usb(home)
                            path_usb_droit_a__l_image = creationdossier_usb(
                                device_node, field="photos/droit_a_l_image"
                            )
                            path_usb_pas_droit_a__l_image = creationdossier_usb(
                                device_node, field="photos/pas_droit_a_l_image"
                            )

                            config_usb += config_usb
                            print(config_usb)

                        timer()
                        os.system(
                            f"gphoto2 --capture-image-and-download --filename {os.environ.get('HOME')}/documents/tmp/capt_%y_%m_%d-%H_%M_%S.jpg"
                        )
                        if os.environ.get("DROIT_A_L_IMAGE"):
                            # on copie l'image dans le dossier droit
                            os.system(
                                f"cp {home}/tmp/*jpg {home}/photos/pas_droit_a_l_image"
                            )
                            if os.environ.get("CLES_USB"):
                                os.system(
                                    f"cp {home}/tmp/*jpg {path_usb_pas_droit_a__l_image}"
                                )

                        else:
                            os.system(
                                f"cp {home}/tmp/*jpg {home}/photos/droit_a_l_image"
                            )
                            if os.environ.get("CLES_USB"):
                                os.system(
                                    f"cp {home}/tmp/*jpg {path_usb_droit_a__l_image}"
                                )

                        path = f"{home}/tmp/{os.listdir(f'{home}/tmp/')[0]}"
                        affichage(path=path)
                        print("fin d'affichage")
                        os.system(f" rm {home}/tmp/*jpg")
                        # Afficher la photo
                        if os.environ.get("PRINT"):
                            print_image()
                            pass

                        if os.environ.get("DOWNLOAD"):
                            download(home, path)
                            # genration qrcode

                        draw_welcome_screen(screen=fenetre)

                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
        else:
            draw_settings_screen(screen=fenetre, toggles=toggles)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
