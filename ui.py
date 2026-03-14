from config import *
from utils import save_params,get_ecran_size,set_environnement_variable
import pygame
import math
import time


def draw_start_button(screen, rect, font):

    mouse = pygame.mouse.get_pos()

    base_color = (80, 180, 255)
    hover_color = (120, 200, 255)

    color = hover_color if rect.collidepoint(mouse) else base_color

    pygame.draw.rect(screen, color, rect, border_radius=20)

    label = font.render("START", True, (0,0,0))
    label_rect = label.get_rect(center=rect.center)

    screen.blit(label, label_rect)

def welcome(screen: pygame.Surface, font_large, font_small):

    pygame.mouse.set_visible(True)

    clock = pygame.time.Clock()

    w, h = screen.get_size()

    vertical_offset = -60

    start_button = pygame.Rect(
        w//2 - 150,
        h//2 + 120,
        300,
        80
    )

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return True

        draw_background(screen)

        camera_img = pygame.image.load("assets/camera.png").convert_alpha()
        camera_img = pygame.transform.smoothscale(camera_img, (140, 140))

        rect = camera_img.get_rect(center=(
            w // 2,
            h // 2 - 120 + vertical_offset
        ))

        screen.blit(camera_img, rect)

        title = font_large.render("Photomaton", True, (255,255,255))
        title_rect = title.get_rect(center=(
            w // 2,
            h // 2 - 20 + vertical_offset
        ))
        screen.blit(title, title_rect)

        text = font_small.render(
            "Touchez START pour prendre une photo",
            True,
            (220,220,220)
        )

        text_rect = text.get_rect(center=(
            w // 2,
            h // 2 + 50 + vertical_offset
        ))

        screen.blit(text, text_rect)

        draw_start_button(screen, start_button, font_small)

        pygame.display.flip()
        clock.tick(60)

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

def decompte(screen, font):

    for i in [5,4,3,2,1]:

        screen.fill((0,0,0))

        text = font.render(str(i), True, (255,255,255))
        rect = text.get_rect(center=screen.get_rect().center)

        screen.blit(text, rect)

        pygame.display.flip()

        pygame.time.wait(1000)

def draw_print_choice_screen(screen: pygame.Surface, font):

    clock = pygame.time.Clock()

    w, h = screen.get_size()

    yes_button = pygame.Rect(w//2 - 220, h//2 + 40, 180, 80)
    no_button  = pygame.Rect(w//2 + 40,  h//2 + 40, 180, 80)

    running = True

    while running:

        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                if yes_button.collidepoint(mouse):
                    running = False
                    return True

                if no_button.collidepoint(mouse):
                    running = False
                    return False

        screen.fill((15,15,20))

        title = font.render("Imprimer la photo ?", True, (255,255,255))
        title_rect = title.get_rect(center=(w//2, h//2 - 80))
        screen.blit(title, title_rect)

        yes_color = (100,220,120) if yes_button.collidepoint(mouse) else (70,170,90)
        no_color  = (220,100,100) if no_button.collidepoint(mouse) else (170,70,70)

        pygame.draw.rect(screen, yes_color, yes_button, border_radius=15)
        pygame.draw.rect(screen, no_color, no_button, border_radius=15)

        yes_text = font.render("OUI", True, (0,0,0))
        no_text  = font.render("NON", True, (0,0,0))

        screen.blit(yes_text, yes_text.get_rect(center=yes_button.center))
        screen.blit(no_text,  no_text.get_rect(center=no_button.center))

        pygame.display.flip()
        clock.tick(60)

def draw_print_screen(screen: pygame.Surface, font_small):

    screen.fill((20, 20, 25))

    w, h = screen.get_size()

    printer_img = pygame.image.load("assets/printer.png").convert_alpha()
    printer_img = pygame.transform.smoothscale(printer_img, (120, 120))

    dots = int(time.time() * 2) % 4
    message = "Impression" + "." * dots
    text = font_small.render(message, True, (255, 255, 255))

    spacing = 30

    total_height = printer_img.get_height() + spacing + text.get_height()

    start_y = (h - total_height) // 2

    image_rect = printer_img.get_rect(
        center=(w // 2, start_y + printer_img.get_height() // 2)
    )

    text_rect = text.get_rect(
        center=(w // 2, start_y + printer_img.get_height() + spacing + text.get_height() // 2)
    )

    screen.blit(printer_img, image_rect)
    screen.blit(text, text_rect)

    pygame.display.flip()

def affichage_image(path: str, screen: pygame.Surface):
    width,height = get_ecran_size(screen=screen)
    screen.fill(BLACK)
    affichage = pygame.image.load(path).convert()
    screen.blit(pygame.transform.scale(affichage, (width, height)), (0, 0))
    pygame.display.flip()

def settings(screen, params, font):

    pygame.mouse.set_visible(True)

    running = True
    toggle_rects = {}

    screen_width, screen_height = screen.get_size()

    title_font = pygame.font.Font(None, 90)

    validate_button = pygame.Rect(
        screen_width // 2 - 120,
        screen_height - 120,
        240,
        70
    )

    while running:

        draw_background(screen)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                mouse = pygame.mouse.get_pos()

                for key, rect in toggle_rects.items():
                    if rect.collidepoint(mouse):
                        params[key]["value"] = not params[key]["value"]

                if validate_button.collidepoint(mouse):
                    save_params(params)
                    set_environnement_variable(params)
                    running = False

        toggle_rects.clear()

        title = title_font.render("Paramètres", True, (255,255,255))
        title_rect = title.get_rect(center=(screen_width//2, 80))
        screen.blit(title, title_rect)
        
        card_width = 700
        card_height = 70

        start_y = 180
        spacing = 100

        for i, (key, data) in enumerate(params.items()):

            y = start_y + i * spacing
            x = (screen_width - card_width) // 2

            card = pygame.Rect(x, y, card_width, card_height)

            pygame.draw.rect(
                screen,
                (40,40,40),
                card,
                border_radius=15
            )

            label = font.render(data["label"], True, (255,255,255))
            label_rect = label.get_rect(
                midleft=(x + 30, y + card_height//2)
            )

            screen.blit(label, label_rect)

            toggle = draw_toggle_switch(
                screen,
                (x + card_width - 110, y + 17),
                data["value"]
            )

            toggle_rects[key] = toggle

        draw_button(screen, validate_button, "VALIDER", font)

        pygame.display.flip()

def draw_background(screen):

    width, height = screen.get_size()

    for y in range(height):

        color = (
            20 + y // 15,
            20 + y // 15,
            30 + y // 10
        )

        pygame.draw.line(screen, color, (0, y), (width, y))

def draw_button(screen, rect, text, font):

    mouse = pygame.mouse.get_pos()

    base_color = (80, 180, 255)
    hover_color = (120, 200, 255)

    color = hover_color if rect.collidepoint(mouse) else base_color

    pygame.draw.rect(screen, color, rect, border_radius=12)

    label = font.render(text, True, (0,0,0))
    label_rect = label.get_rect(center=rect.center)

    screen.blit(label, label_rect)

def draw_toggle_switch(screen, position, state):

    x, y = position
    width, height = 70, 36
    radius = height // 2

    color_on = (0, 200, 120)
    color_off = (120, 120, 120)

    bg_color = color_on if state else color_off

    pygame.draw.rect(
        screen,
        bg_color,
        (x, y, width, height),
        border_radius=radius
    )

    knob_x = x + width - radius if state else x + radius

    pygame.draw.circle(
        screen,
        (255, 255, 255),
        (knob_x, y + radius),
        radius - 3
    )

    return pygame.Rect(x, y, width, height)