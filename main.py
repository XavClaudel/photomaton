import pygame
import os
from config import *
from ui import settings,welcome,decompte, screen_usb ,draw_print_choice_screen,draw_print_screen,affichage_image
from usb import detect_existing_usb,detect_usb_event,wait_for_mount,copy_photos_to_usb
from camera import take_picture
from printer import print_picture
from qr import generate_qr_code
from utils import create_dir
import time
import pyudev
from hotspot import create_hotspot
from webserver import start_server
import threading

running = True
context = pyudev.Context()

monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem="block")
monitor.start()
pygame.init()
create_hotspot('photomaton', 'photomaton')
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
pygame.display.set_caption("Photomaton")
FONT_LARGE = pygame.font.Font(None, 120)
FONT_SMALL = pygame.font.Font(None, 50)
create_dir(PHOTO_DIR)
create_dir(TMP_DIR)
server_thread = threading.Thread(target=start_server)
server_thread.start()

print("Serveur lancé")

count_run =0
while running:

    if count_run == 0:
        settings(font=FONT_SMALL,params=PARAMS,screen=screen)

    if os.environ.get("CLES_USB") and count_run == 0:
        
        running_usb = True
        device, mount = detect_existing_usb()

        if mount:
            mount_path = mount
            running_usb = False
        while running_usb:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen_usb(screen=screen, font_large=FONT_LARGE)

            device = detect_usb_event(monitor)

            if device:

                mount_path = wait_for_mount(device)

                if mount_path:
                    running_usb = False
    
    welcome(font_large=FONT_LARGE,font_small=FONT_SMALL,screen=screen)
    count_run += 1
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    decompte(screen=screen)
                    photo_path=take_picture(tmp_dir=TMP_DIR)
                    affichage_image(path=photo_path, screen=screen)
                    time.sleep(8)
                    if os.environ.get("CLES_USB"):
                        copy_photos_to_usb(photo_path=photo_path,usb_mount=mount_path)
                    if os.environ.get("IMPRIMER"):
                        while True:
                            button_pressed = False
                            draw_print_choice_screen(screen=screen,font_small=FONT_SMALL)
                            start_time = time.time()
                            while time.time() - start_time < 10:
                                for event in pygame.event.get():
                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_p:
                                            button_pressed = True
                                            draw_print_screen(screen=screen,font_small=FONT_SMALL)
                                            print_picture(path=str(photo_path))
                                            time.sleep(60)

                                    break
                            if not button_pressed:
                                break

                    if os.environ.get("QR_CODE"):
                        generate_qr_code()
                    #EFFACER TMP
                    #shutil.rmtree(TMP_DIR)
    count_run =+ 1