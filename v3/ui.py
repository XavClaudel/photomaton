import pygame

WHITE = (255,255,255)
BLACK = (0,0,0)

def welcome(screen, font_big, font_small):

    screen.fill(BLACK)

    title = font_big.render("Bienvenue", True, WHITE)
    text = font_small.render("Appuyez sur le bouton", True, WHITE)

    screen.blit(title,(300,100))
    screen.blit(text,(300,300))

    pygame.display.flip()