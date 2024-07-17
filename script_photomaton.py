import pygame
import time
import os
import sys


def timer():
    fenetre = pygame.display.set_mode((640, 480))
    for i in range(5, -1, -1):
        decompte = pygame.image.load(f"images/{i}.jpg").convert()
        fenetre.blit(pygame.transform.scale(decompte, (640, 480)), (0, 0))
        pygame.display.flip()
        time.sleep(1)


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

# Appels de la fonction pour chaque cas


def draw_toggle_switch(screen, position, state):
    pygame.draw.rect(screen, (255, 255, 255), (*position, 60, 30), border_radius=15)
    if state:
        pygame.draw.circle(screen, (0, 255, 0), (position[0] + 45, position[1] + 15), 15)
    else:
        pygame.draw.circle(screen, (255, 0, 0), (position[0] + 15, position[1] + 15), 15)

def show_popup(screen, toggles):
    font = pygame.font.Font(None, 50)
    screen.fill((0, 0, 0))
    params = ["Paramètre 1", "Paramètre 2", "Paramètre 3"]
    for i, param in enumerate(params):
        text = font.render(param, 1, (255, 255, 255))
        screen.blit(text, (100, 100 + i * 100))
        draw_toggle_switch(screen, (400, 100 + i * 100), toggles[i])
    pygame.display.flip()

def bienvenue():
    droit_a_l_image = False
    pygame.init()
    fenetre = pygame.display.set_mode((640, 480))
    font = pygame.font.Font(None, 120)
    font1 = pygame.font.Font(None, 50)
    icon = pygame.image.load("images/settings.png")  # Assurez-vous d'avoir une icône nommée "icon.png"
    icon_rect = icon.get_rect(topleft=(600, 0))

    running = True
    show_popup_window = False
    toggles = [False, False, False]  # Initial states of the toggle switches

    while running:
        fenetre.fill((0, 0, 0))
        if droit_a_l_image:
            text = font.render("Bienvenue", 1, (255, 255, 255))
            text1 = font1.render("Appuyer sur le bouton vert", 1, (255, 255, 255))
            text2 = font1.render("pour céder votre droits à l'image", 1, (255, 255, 255))
            text3 = font1.render("Sinon appuyer sur le bouton rouge", 1, (255, 255, 255))
            fenetre.blit(text, (100, 0))
            fenetre.blit(text1, (15, 150))
            fenetre.blit(text2, (15, 200))
            fenetre.blit(text3, (15, 300))

        fenetre.blit(icon, icon_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if icon_rect.collidepoint(event.pos):
                    show_popup_window = not show_popup_window
                elif show_popup_window:
                    for i in range(len(toggles)):
                        toggle_rect = pygame.Rect(400, 100 + i * 100, 60, 30)
                        if toggle_rect.collidepoint(event.pos):
                            toggles[i] = not toggles[i]

        if show_popup_window:
            show_popup(fenetre, toggles)

def init():
    os.environ.get("DROIT_A_L_IMAGE", False)
    os.environ.get("PRINT", False)
    os.environ.get("DOWNLOAD", False)
    # création des dossiers
    creationdossier("documents/photos/droit_a_l_image")
    creationdossier("documents/photos/pas_droit_a_l_image")
    creationdossier("documents/tmp")
    # montage de la clés


# TODO settings
# def settings():
# 	#mise en place de la demande de droit à l'image
# 	# impression
# 	#téléchargement

def print_image():
    pass

def download():
    pass

def affichage (path) :
	#affichage de l'image
	#fenetre = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
    fenetre = pygame.display.set_mode((640, 480))
    affichage = pygame.image.load(f"{path}").convert()
    fenetre.blit(pygame.transform.scale(affichage, (640, 480)), (0, 0))
    pygame.display.flip()
    time.sleep (5)

pygame.init()
init()
bienvenue()
while True:
    # retour écran
    for event in pygame.event.get():  # Attente des événements
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # Si "a" est  préssée
                home = f"{os.environ.get("HOME")}/documents"
                timer()
                os.system(
                    f"gphoto2 --capture-image-and-download --filename {os.environ.get('HOME')}/documents/tmp/capt_%y_%m_%d-%H_%M_%S.jpg"
                )
                if os.environ.get("DROIT_A_L_IMAGE"):
                    # on copie l'image dans le dossier droit
                    os.system(f"cp {home}/tmp/*jpg {home}/photos/pas_droit_a_l_image")
                else:
                    os.system(f"cp {home}/tmp/*jpg {home}/photos/droit_a_l_image")


                affichage(f"{home}/tmp/{os.listdir(f"{home}/tmp/")[0]}")
                os.system(f" rm {home}/tmp/*jpg")
                #Afficher la photo 
                if  os.environ.get("PRINT"):
                    print_image()
                    pass
   
                if  os.environ.get("DOWNLOAD"):
                    pass
                    #genration qrcode
                
                bienvenue()



            # if event.key == pygame.K_z: #Si "z" est préssé
            # 	timer ()
            # 	os.system ("mount /dev/sda1 /media/pi/PHOTO")
            # 	creationdossierpasdroit ()
            # 	#prise de photo
            # 	os.system("gphoto2 --capture-image-and-download --filename /home/xav/Nextcloud/dev/photomaton/script_affichage/ordi/avec_choix_droit_a_l_image/test/photos/tmp/capt_%y_%m_%d-%H_%M_%S.jpg")
            # 	#on copie l'image dans le dossier pas droits
            # 	os.system ("cp /home/xav/Nextcloud/dev/photomaton/script_affichage/ordi/avec_choix_droit_a_l_image/test/photos/tmp/*jpg /home/xav/Nextcloud/dev/photomaton/script_affichage/ordi/avec_choix_droit_a_l_image/test/photos/pasdroits")
            # 	#on renomme l'image
            # 	os.system ("mv /home/xav/Nextcloud/dev/photomaton/script_affichage/ordi/avec_choix_droit_a_l_image/test/photos/tmp/*jpg /home/xav/Nextcloud/dev/photomaton/script_affichage/ordi/avec_choix_droit_a_l_image/test/photos/tmp/1.jpg")
            # 	fenetre = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
            # 	affichage ()
            # 	time.sleep (3)
            # 	#démontage de la clé
            # 	os.system ("umount /media/pi/PHOTO")
            # 	#on supprime l'image du fichier tmp
            # 	os.system (" rm /home/xav/Nextcloud/dev/photomaton/script_affichage/ordi/avec_choix_droit_a_l_image/test/photos/tmp/1.jpg")
            # 	merci ()
            # 	bienvenue ()
            if event.key == pygame.K_e:  # Si "e" est préssé
                # quitter les fenêtres
                pygame.quit()
