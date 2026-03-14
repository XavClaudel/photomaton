import pygame
import os
from config import *
from ui import settings,welcome,decompte, screen_usb ,draw_print_choice_screen,draw_print_screen,affichage_image
from usb import detect_existing_usb,detect_usb_event,wait_for_mount,copy_photos_to_usb
from camera import take_picture
from printer import impression_photo
from qr import generate_qr_code
from utils import create_dir,copy_photos_to_local
import time
import pyudev
from hotspot import create_hotspot
from webserver import start_server



running = True
context = pyudev.Context()
HOTSPOT = False
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem="block")
monitor.start()
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
pygame.display.set_caption("Photomaton")
FONT_LARGE = pygame.font.Font(None, 120)
FONT_SMALL = pygame.font.Font(None, 50)
create_dir(PHOTO_DIR)
create_dir(TMP_DIR)



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

            device = detect_usb_event(monitor=monitor)

            if device:

                mount_path = wait_for_mount(device=device)

                if mount_path:
                    running_usb = False
    if os.environ.get("IMPRIMER") and count_run == 0:
        print("création du hotspot")
        create_hotspot('photomaton', 'photomaton')
    welcome(screen=screen,font_large=FONT_LARGE,font_small=FONT_SMALL)

    decompte(screen=screen,font=FONT_SMALL)

    photo_path = take_picture(tmp_dir=TMP_DIR)
    copy_photos_to_local(photo_path=photo_path)
    start_time = time.time()
    while time.time() - start_time < 10:
        affichage_image(path=photo_path, screen=screen)
    if os.environ.get("CLES_USB"):
        copy_photos_to_usb(photo_path=photo_path,usb_mount=mount_path)
    if os.environ.get("IMPRIMER"):
          running_impression = True
          while running_impression:
            choice = draw_print_choice_screen(screen=screen,font=FONT_SMALL)
            if choice:    
                impression_photo(screen=screen,path=str(photo_path),font=FONT_SMALL)
                    
            else:
               running_impression = False 

    count_run =+ 1

