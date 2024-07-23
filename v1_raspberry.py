import os
import time
import pygame
import sys
import pyudev
import subprocess
import qrcode
from concurrent.futures import ThreadPoolExecutor
import RPi.GPIO as GPIO

# Déclaration des ports GPIO que l'on utilise
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialisation de Pygame
pygame.init()

# Définition des dimensions de la fenêtre
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Multi-écrans avec Pygame")

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
env_vars = ["DROIT_A_L_IMAGE", "PRINT", "DOWNLOAD", "CLES_USB"]
toggles = [os.getenv(var) == "TRUE" for var in env_vars]

def draw_settings_screen(screen, toggles):
    screen.fill(BLACK)
    params = ["DROIT_A_L_IMAGE", "PRINT", "DOWNLOAD", "CLES_USB"]
    for i, param in enumerate(params):
        text = font_small.render(param, 1, WHITE)
        screen.blit(text, (100, 100 + i * 100))
        draw_toggle_switch(screen, (450, 100 + i * 100), toggles[i])
    pygame.display.flip()

def draw_toggle_switch(screen, position, state):
    pygame.draw.rect(screen, WHITE, (*position, 60, 30), border_radius=15)
    if state:
        pygame.draw.circle(screen, GREEN, (position[0] + 45, position[1] + 15), 15)
    else:
        pygame.draw.circle(screen, RED, (position[0] + 15, position[1] + 15), 15)

def set_environment_variable(index, state):
    os.environ[env_vars[index]] = "TRUE" if state else "FALSE"

def draw_welcome_screen(screen):
    screen.fill(BLACK)
    text = font_large.render("Bienvenue", 1, WHITE)
    if os.environ.get("DROIT_A_L_IMAGE"):
        text1 = font_small.render("Appuyer sur le bouton vert", 1, WHITE)
        text2 = font_small.render("pour céder votre droits à l'image", 1, WHITE)
        text3 = font_small.render("Sinon appuyer sur le bouton rouge", 1, WHITE)
        screen.blit(text, (100, 0))
        screen.blit(text1, (100, 150))
        screen.blit(text2, (100, 200))
        screen.blit(text3, (100, 300))
    else:
        text1 = font_small.render("Appuyer sur le déclencheur", 1, WHITE)
        text2 = font_small.render("pour prendre une photo", 1, WHITE)
        screen.blit(text, (100, 0))
        screen.blit(text1, (100, 150))
        screen.blit(text2, (100, 200))
    pygame.display.flip()

def timer():
    for i in range(5, -1, -1):
        fenetre = pygame.display.set_mode((width, height))
        decompte = pygame.image.load(f"images/{i}.jpg").convert()
        fenetre.blit(pygame.transform.scale(decompte, (width, height)), (0, 0))
        pygame.display.flip()
        time.sleep(1)

def affichage(path):
    fenetre = pygame.display.set_mode((width, height))
    affichage = pygame.image.load(path).convert()
    fenetre.blit(pygame.transform.scale(affichage, (width, height)), (0, 0))
    pygame.display.flip()
    time.sleep(5)

def draw_print_screen(screen):
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
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (100, 150 + i * 50))
    pygame.display.flip()


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



def init():
    os.environ.get("DROIT_A_L_IMAGE", False)
    os.environ.get("PRINT", False)
    os.environ.get("DOWNLOAD", False)
    os.environ.get("CLES_USB", False)
    creationdossier("documents/photos/droit_a_l_image")
    creationdossier("documents/photos/pas_droit_a_l_image")
    creationdossier("documents/tmp")    
def main():
    global show_image, start_time, image_path

    init()
    running = True
    running_print = False
    in_welcome_screen = True
    config_usb = 1
    DECLENCHEUR = False
    PRINT_IMAGE = False
    show_image = False
    start_time = None

    while running:
        etat_declencheur = GPIO.input(2)
        etat_print = GPIO.input(3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z or etat_declencheur == 0:
                    in_welcome_screen = not in_welcome_screen
                    DECLENCHEUR = True
            elif event.type == pygame.MOUSEBUTTONDOWN and not in_welcome_screen:
                for i in range(len(toggles)):
                    toggle_rect = pygame.Rect(450, 100 + i * 100, 60, 30)
                    if toggle_rect.collidepoint(event.pos):
                        toggles[i] = not toggles[i]
                        set_environment_variable(i, toggles[i])

        if in_welcome_screen:
            draw_welcome_screen(screen)
            
            if etat_declencheur == 0 and DECLENCHEUR:
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

                timer()
                os.system(
                    f"gphoto2 --capture-image-and-download --filename {os.environ.get('HOME')}/documents/tmp/capt_%y_%m_%d-%H_%M_%S.jpg"
                )
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
                affichage(path=path)
                time.sleep(5)
                print("fin d'affichage")
                            

                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        else:
            draw_settings_screen(screen, toggles)

        if show_image and time.time() - start_time >= 5:
            if os.getenv("PRINT_IMAGE", "false").lower() == "true":
                draw_print_screen(screen)
                start_time = time.time()
                while time.time() - start_time < 10:
                    if GPIO.input(3) == 0:
                        os.system(f'lp -d Canon_SELPHY_CP1500 {path}')
                        time.sleep(60)
                        os.system(f"rm {home}/tmp/*jpg")
                        break
                else:
                    show_image = False
                    in_welcome_screen = True
                    draw_welcome_screen(screen)
            else:
                show_image = False
                in_welcome_screen = True
                draw_welcome_screen(screen)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
