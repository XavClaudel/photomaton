import os
import time
import pygame
import RPi.GPIO as GPIO
import subprocess
import pyudev

# Initialisation des GPIO
GPIO.setmode(GPIO.BCM)
BUTTON_PIN_2 = 2
BUTTON_PIN_3 = 3
GPIO.setup(BUTTON_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variables d'environnement
env_vars = ["DROIT_A_L_IMAGE", "PRINT", "DOWNLOAD", "CLES_USB"]

# États initiaux des boutons glissants
toggles = [os.getenv(var) == "TRUE" for var in env_vars]

# Initialisation de Pygame
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("PHOTOMATON")

# Définition des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

#Polices
font_large = pygame.font.Font(None, 120)
font_small = pygame.font.Font(None, 50)

# Variables d'état
show_image = False
print_image = os.getenv('PRINT_IMAGE', 'false').lower() == 'true'
start_time = None

# Fonction pour récupérer une image
def get_image():
    global show_image, start_time
    # Ici vous pouvez ajouter le code pour capturer ou charger l'image
    show_image = True
    start_time = time.time()
    print("Image captured")

# Fonction pour imprimer l'image
def print_picture():
    print("Printing image...")

def draw_settings_screen(screen:pygame, toggles:list):
    screen.fill(BLACK)
    params = ["DROIT_A_L_IMAGE", "PRINT", "DOWNLOAD", "CLES_USB"]
    for i, param in enumerate(params):
        text = font_small.render(param, 1, WHITE)
        screen.blit(text, (100, 100 + i * 100))
        draw_toggle_switch(screen=screen, position=(450, 100 + i * 100), state=toggles[i])
    pygame.display.flip()

def draw_toggle_switch(screen:pygame, position:tuple, state:list):
    pygame.draw.rect(screen, WHITE, (*position, 60, 30), border_radius=15)
    if state:
        pygame.draw.circle(screen, GREEN, (position[0] + 45, position[1] + 15), 15)
    else:
        pygame.draw.circle(screen, RED, (position[0] + 15, position[1] + 15), 15)

def set_environment_variable(index:int, state:list):
    os.environ[env_vars[index]] = "TRUE" if state else "FALSE"

def draw_welcome_screen(screen:pygame):
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
        screen.blit(text1, (100, 150))
        screen.blit(text2, (100, 200))
        screen.blit(text3, (100, 300))
    else:
        text1 = font_small.render("Appuyer sur le déclencheur", 1, (255, 255, 255))
        text2 = font_small.render("pour prendre une photo", 1, (255, 255, 255))
        screen.blit(text, (100, 0))
        screen.blit(text1, (100, 150))
        screen.blit(text2, (100, 200))

    pygame.display.flip()
def timer():
    fenetre = pygame.display.set_mode((width, height))
    for i in range(5, -1, -1):
        decompte = pygame.image.load(f"images/{i}.jpg").convert()
        fenetre.blit(pygame.transform.scale(decompte, (width, height)), (0, 0))
        pygame.display.flip()
        time.sleep(1)


def affichage(path:str):
    # affichage de l'image
    fenetre = pygame.display.set_mode((width, height))
    affichage = pygame.image.load(path).convert()
    fenetre.blit(pygame.transform.scale(affichage, (width, height)), (0, 0))
    pygame.display.flip()
    time.sleep(5)



def mount_usb(device_node : str, mount_point : str):
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


def monitor_usb(home:str) -> str:
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

def init():
    os.environ.get("DROIT_A_L_IMAGE", False)
    os.environ.get("PRINT", False)
    os.environ.get("DOWNLOAD", False)
    os.environ.get("CLES_USB", False)
    creationdossier("documents/photos/droit_a_l_image")
    creationdossier("documents/photos/pas_droit_a_l_image")
    creationdossier("documents/tmp")    

def creationdossier(sous_chemin:str):
    home_dir = os.getenv("HOME")  # Récupérer la variable d'environnement HOME
    if home_dir is None:
        raise EnvironmentError("La variable d'environnement HOME n'est pas définie.")

    dir_path = os.path.join(home_dir, sous_chemin)  # Chemin complet du dossier

    if not os.path.exists(dir_path):  # Vérifier si le dossier n'existe pas
        os.makedirs(dir_path)  # Créer le dossier
        print(f"Le dossier '{dir_path}' a été créé.")
    else:
        print(f"Le dossier '{dir_path}' existe déjà.")


def creationdossier_usb(device_node:str, field:str) ->str:
    home_dir = f"/media/{device_node.split('/')[2]}/{field}"  # Récupérer la variable d'environnement HOME
    if home_dir is None:
        raise EnvironmentError("La variable d'environnement HOME n'est pas définie.")

    if not os.path.exists(home_dir):  # Vérifier si le dossier n'existe pas
        os.makedirs(home_dir)  # Créer le dossier
        print(f"Le dossier '{home_dir}' a été créé.")
    else:
        print(f"Le dossier '{home_dir}' existe déjà.")

    return home_dir
    
def draw_print_screen(path :str,screen:pygame):
    lines = [
    "Voulez-vous imprimez",
    "cette photo ?",
    "",
    "Si oui, appuyer sur P",
    "",
    "Si non, appuyer sur N"
]
    screen.fill(BLACK)
    for i, line in enumerate(lines):
        text_surface = font_small.render(line, True, WHITE)
        screen.blit(text_surface, (100, 150 + i * 50))


    pygame.display.flip()
def main():
    init()
    global show_image, start_time
    config_usb = True
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z :
                    in_welcome_screen = not in_welcome_screen
                    DECLENCHEUR = True
            elif event.type == pygame.MOUSEBUTTONDOWN and not in_welcome_screen:
                for i in range(len(toggles)):
                    toggle_rect = pygame.Rect(450, 100 + i * 100, 60, 30)
                    if toggle_rect.collidepoint(event.pos):
                        toggles[i] = not toggles[i]
                        set_environment_variable(i, toggles[i])

        # Vérifiez les boutons GPIO
        if GPIO.input(BUTTON_PIN_2) == GPIO.LOW:
            home = f"{os.environ.get('HOME')}/documents"
            if os.environ.get("CLES_USB") and config_usb :
                print("cles_usb")
                device_node = monitor_usb(home)
                path_usb_droit_a__l_image = creationdossier_usb(
                        device_node, field="photos/droit_a_l_image"
                    )
                path_usb_pas_droit_a__l_image = creationdossier_usb(
                        device_node, field="photos/pas_droit_a_l_image"
                    )

                config_usb = False
                timer()
                os.system(
                    f"gphoto2 --capture-image-and-download --filename {os.environ.get('HOME')}/documents/tmp/capt_%y_%m_%d-%H_%M_%S.jpg"
                )
                time.sleep(0.3)  # Anti-rebond
                if os.environ.get("DROIT_A_L_IMAGE"):
                    # on copie l'image dans le dossier droit
                    os.system(f"cp {home}/tmp/*jpg {home}/photos/pas_droit_a_l_image")
                    if os.environ.get("CLES_USB"):
                        os.system(f"cp {home}/tmp/*jpg {path_usb_pas_droit_a__l_image}")

                else:
                    os.system(f"cp {home}/tmp/*jpg {home}/photos/droit_a_l_image")
                    if os.environ.get("CLES_USB"):
                        os.system(f"cp {home}/tmp/*jpg {path_usb_droit_a__l_image}")

                path = f"{home}/tmp/{os.listdir(f'{home}/tmp/')[0]}"
            

        if show_image and time.time() - start_time >= 5:
            if print_image:
                screen.fill(WHITE)
                text = font_small.render("Impression", True, BLACK)
                screen.blit(text, (250, 250))
                pygame.display.flip()

                start_time = time.time()
                while time.time() - start_time < 10:
                    if GPIO.input(BUTTON_PIN_3) == GPIO.LOW:
                        print_picture()
                        time.sleep(0.3)  # Anti-rebond
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                    time.sleep(0.1)
            show_image = False
            start_time = None

        # Écran d'accueil
        if not show_image:
            screen.fill(WHITE)
            text = font_small.render("Bienvenue", True, BLACK)
            screen.blit(text, (250, 250))
            pygame.display.flip()

        # Afficher l'image pendant 5 secondes
        if show_image:
            # affichage de l'image
            fenetre = pygame.display.set_mode((width, height))
            affichage = pygame.image.load(path).convert()
            fenetre.blit(pygame.transform.scale(affichage, (width, height)), (0, 0))
            pygame.display.flip()

        time.sleep(0.1)

    pygame.quit()
    GPIO.cleanup()

if __name__ == "__main__":
    main()