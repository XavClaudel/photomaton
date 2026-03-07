import pygame
import time

from config import *
from camera import capture_photo
from printer import print_picture
from display import init_display
from utils import create_dir


def main():

    create_dir(PHOTO_DIR)
    create_dir(TMP_DIR)

    screen = init_display()

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        # déclenchement photo
        path = capture_photo(TMP_DIR)

        print("Photo prise :", path)

        # affichage
        img = pygame.image.load(path)

        screen.blit(img, (0,0))
        pygame.display.flip()

        time.sleep(5)

        print_picture(path)


if __name__ == "__main__":
    main()