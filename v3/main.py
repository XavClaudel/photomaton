import pygame
import RPi.GPIO as GPIO
import time

from config import *
from camera import capture_image
from printer import print_photo
from utils import create_dir
from ui import welcome

pygame.init()

screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

font_big = pygame.font.Font(None,120)
font_small = pygame.font.Font(None,50)

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

create_dir(PHOTO_DIR)
create_dir(TMP_DIR)

running = True

while running:

    welcome(screen, font_big, font_small)

    if GPIO.input(BUTTON_PIN) == GPIO.LOW:

        for i in range(COUNTDOWN,0,-1):

            screen.fill((0,0,0))

            text = font_big.render(str(i),True,(255,255,255))

            screen.blit(text,(600,300))

            pygame.display.flip()

            time.sleep(1)

        path = capture_image(TMP_DIR)

        print("Photo:",path)

        img = pygame.image.load(str(path))
        screen.blit(pygame.transform.scale(img,screen.get_size()),(0,0))

        pygame.display.flip()

        time.sleep(DISPLAY_TIME)

        print_photo(path)