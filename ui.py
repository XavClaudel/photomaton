from config import *
from utils import save_params,get_ecran_size,set_environnement_variable
import pygame
import time
import math


def welcome(screen: pygame.Surface, font_large, font_small):

    screen.fill(BLACK)

    w, h = screen.get_size()

    title = font_large.render("Bienvenue", True, WHITE)
    text = font_small.render("Appuyez sur le bouton", True, WHITE)

    total_height = title.get_height() + 40 + text.get_height()
    start_y = (h - total_height) // 2

    title_rect = title.get_rect(center=(w//2, start_y + title.get_height()//2))
    text_rect = text.get_rect(center=(w//2, start_y + title.get_height() + 40 + text.get_height()//2))

    screen.blit(title, title_rect)
    screen.blit(text, text_rect)

    pygame.display.flip()


def screen_usb(screen: pygame.Surface, font_large):
    usb_icon = pygame.image.load("assets/usb.png").convert_alpha()
    screen.fill(BLACK)

    w, h = screen.get_size()

    title = font_large.render("BRANCHEZ", True, WHITE)
    text = font_large.render("UNE CLÉ USB", True, WHITE)

    title_rect = title.get_rect(center=(w//2, h//3))
    text_rect = text.get_rect(center=(w//2, h//3 + 120))

    screen.blit(title, title_rect)
    screen.blit(text, text_rect)

    time = pygame.time.get_ticks() / 500
    scale = 1 + 0.1 * math.sin(time)

    new_size = int(120 * scale)
    icon = pygame.transform.smoothscale(usb_icon, (new_size, new_size))

    icon_rect = icon.get_rect(center=(w//2, h//3 + 280))

    screen.blit(icon, icon_rect)

    pygame.display.flip()


def draw_toggle_switch(screen:pygame.Surface, position:tuple, state:str):
    x, y = position
    width, height = 60, 30
    radius = height // 2

    bg_color = GREEN if state else RED
    pygame.draw.rect(screen, bg_color, (x, y, width, height), border_radius=radius)

    knob_x = x + width - radius if state else x + radius
    pygame.draw.circle(screen, WHITE, (knob_x, y + radius), radius - 3)

    return pygame.Rect(x, y, width, height)


def draw_button(screen:pygame.Surface, text:str, rect, font):
    pygame.draw.rect(screen, BLACK, rect, border_radius=8)
    label = font.render(text, True, WHITE)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def settings(screen:pygame.Surface, params: dict, font):

    pygame.mouse.set_visible(True)

    running = True
    toggle_rects = {}

    screen_width, screen_height = screen.get_size()

    validate_button = pygame.Rect(
        screen_width - 200,
        screen_height - 80,
        150,
        50
    )
    
    while running:

        screen.fill((0,0,0))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                mouse_pos = pygame.mouse.get_pos()

                for key, rect in toggle_rects.items():
                    if rect.collidepoint(mouse_pos):
                        params[key]["value"] = not params[key]["value"]

                if validate_button.collidepoint(mouse_pos):
                    save_params(params=params)
                    set_environnement_variable(settings=params)
                    running = False

        toggle_rects.clear()

        start_y = 120
        spacing = 80

        for i, (key, data) in enumerate(params.items()):

            y = start_y + i * spacing

            text = font.render(data["label"], True, (255,255,255))
            screen.blit(text, (100, y))

            rect = draw_toggle_switch(screen=screen, position=(450, y), state=data["value"])

            toggle_rects[key] = rect

        draw_button(screen=screen, text="Valider", rect=validate_button, font=font)
        pygame.display.flip()


def decompte(screen:pygame.Surface):
    width,height = get_ecran_size(screen=screen)
    for i in range(5, 0, -1):
        decompte = pygame.image.load(f"{PWD}/assets/{i}.jpg").convert()
        screen.blit(pygame.transform.scale(decompte, (width, height)), (0, 0))
        pygame.display.flip()
        time.sleep(1)
    decompte = pygame.image.load("assets/0.jpg").convert()
    screen.blit(pygame.transform.scale(decompte, (width, height)), (0, 0))
    pygame.display.flip()


def draw_print_choice_screen(screen: pygame.Surface,font_small):
    lines = [
        "Voulez-vous imprimez",
        "cette photo ?",
        "",
        "Si oui, appuyer sur le déclencheur.",
        "",
        "Si non, attendez.",
    ]
    screen.fill(BLACK)
    for i, line in enumerate(lines):
        text_surface = font_small.render(line, True, WHITE)
        screen.blit(text_surface, (180, 150 + i * 50))

    pygame.display.flip()


def draw_print_screen(screen: pygame.Surface,font_small):
    screen.fill(BLACK)
    text = font_small.render("Impression", True, WHITE)
    screen.blit(text, (350, 250))
    pygame.display.flip()


def affichage_image(path: str, screen: pygame.Surface):
    width,height = get_ecran_size(screen=screen)
    # affichage de l'image
    screen.fill(BLACK)
    affichage = pygame.image.load(path).convert()
    screen.blit(pygame.transform.scale(affichage, (width, height)), (0, 0))
    pygame.display.flip()