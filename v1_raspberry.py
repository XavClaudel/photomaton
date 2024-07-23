import os
import time
import pygame
import RPi.GPIO as GPIO

# Initialisation des GPIO
GPIO.setmode(GPIO.BCM)
BUTTON_PIN_2 = 2
BUTTON_PIN_3 = 3
GPIO.setup(BUTTON_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

# Variables d'environnement
env_vars = ["DROIT_A_L_IMAGE", "PRINT", "DOWNLOAD", "CLES_USB"]

# États initiaux des boutons glissants
toggles = [os.getenv(var) == "TRUE" for var in env_vars]
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

def set_environment_variable(index:int, state:list):
    os.environ[env_vars[index]] = "TRUE" if state else "FALSE"

def draw_toggle_switch(screen:pygame, position:tuple, state:list):
    pygame.draw.rect(screen, WHITE, (*position, 60, 30), border_radius=15)
    if state:
        pygame.draw.circle(screen, GREEN, (position[0] + 45, position[1] + 15), 15)
    else:
        pygame.draw.circle(screen, RED, (position[0] + 15, position[1] + 15), 15)

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

def affichage(path:str):
    # affichage de l'image
    fenetre = pygame.display.set_mode((width, height))
    affichage = pygame.image.load(path).convert()
    fenetre.blit(pygame.transform.scale(affichage, (width, height)), (0, 0))
    pygame.display.flip()
    time.sleep(5)
    
def main():
    global show_image, start_time

    running = True
    in_welcome_screen = False
    config_usb = 1
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

        if in_welcome_screen:
            draw_welcome_screen(screen=screen)

            # Vérifiez les boutons GPIO
            if GPIO.input(BUTTON_PIN_2) == GPIO.LOW:
                get_image()
                time.sleep(0.3)  # Anti-rebond

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
                draw_welcome_screen(screen=screen)

            # Afficher l'image pendant 5 secondes
            if show_image:
                screen.fill(WHITE)
                # Remplacez par le chargement et l'affichage de votre image
                text = font_small.render("Image affichée", True, BLACK)
                screen.blit(text, (300, 250))
                pygame.display.flip()

            time.sleep(0.1)
        else:
            draw_settings_screen(screen=screen, toggles=toggles)
    pygame.quit()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
