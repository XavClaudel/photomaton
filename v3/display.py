import pygame

pygame.init()

def init_display():

    info = pygame.display.Info()

    screen = pygame.display.set_mode(
        (info.current_w, info.current_h),
        pygame.FULLSCREEN
    )

    return screen