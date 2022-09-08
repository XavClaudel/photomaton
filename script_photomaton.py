#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import time
import os
import sys
import RPi.GPIO as GPIO, time
#d�éclaration et initialisation des ports GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN)
GPIO.setup(3, GPIO.IN)

def timer () :
	#Création de la fenêtre 5
	fenetre = pygame.display.set_mode((720, 420), pygame.FULLSCREEN)
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/5.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (720, 420)), (0, 0))
	pygame.display.flip()
	#Pause
	time.sleep (1)
	#Création de la fenêtre 4
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/4.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (720, 420)), (0, 0))
	pygame.display.flip()
	#Pause
	time.sleep (1)
	#Création de la fenêtre 3
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/3.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (720, 420)), (0, 0))
	pygame.display.flip()
	#Pause
	time.sleep (1)
	#Création de la fenêtre 2
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/2.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (720, 420)), (0, 0))
	pygame.display.flip()
	time.sleep (1)
	#Création de la fenêtre 1
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/1.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (720, 420)), (0, 0))
	pygame.display.flip()
	#Pause
	time.sleep (1)
	#Création de la fenêtre 0
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/0.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (720, 420)), (0, 0))
	pygame.display.flip()
		 
def creationdossierdroit () :
	if (os.path.isdir("/media/pi/PHOTO/photos") == False): # si le dossier pour stocker les photos n'existe pas       
		os.mkdir("/media/pi/PHOTO/photos")                  # alors on crée le dossier 
		os.chmod("/media/pi/PHOTO/photos",0o777)            # et on change les droits pour pouvoir effacer des photos
	if (os.path.isdir("/media/pi/PHOTO/photos/droits") == False): # si le dossier pour stocker les photos n'existe pas       
		os.mkdir("/media/pi/PHOTO/photos/droits")                  # alors on crée le dossier 
		os.chmod("/media/pi/PHOTO/photos/droits",0o777)            # et on change les droits pour pouvoir effacer des photos
	
def creationdossierpasdroit () :
	if (os.path.isdir("/media/pi/PHOTO/photos") == False): # si le dossier pour stocker les photos n'existe pas       
		os.mkdir("/media/pi/PHOTO/photos")                  # alors on crée le dossier 
		os.chmod("/media/pi/PHOTO/photos",0o777)            # et on change les droits pour pouvoir effacer des photos
	if (os.path.isdir("/media/pi/PHOTO/photos/pasdroits") == False): # si le dossier pour stocker les photos n'existe pas       
		os.mkdir("/media/pi/PHOTO/photos/pasdroits")                  # alors on crée le dossier 
		os.chmod("/media/pi/PHOTO/photos/pasdroits",0o777)            # et on change les droits pour pouvoir effacer des photos


#Initialisation de la bibliothèque Pygame
pygame.init()
#Création et affichage de la fenêtre bienvenue
def bienvenue () :
	#création de la fenêtre de bienvenue
	fenetre = pygame.display.set_mode((720, 420),pygame.FULLSCREEN)
	#configuration des fonts
	font=pygame.font.Font(None, 120)
	font1=pygame.font.Font(None,60)
	# configuration première ligne de texte
	text = font.render("Bienvenue",1,(255,255,255))
	#configuration deuxième ligne de texte
	text1 = font1.render("Appuyer sur le bouton 1",1, (255,255,255))
	#configration troisième ligne de texte
	text2 = font1.render(u"pour céder votre droits à l'image",1, (255,255,255))
	#configuration quatrième ligne de texte
	text3 = font1.render("Sinon appuyer sur le bouton 2",1, (255,255,255))
	#affichage première ligne de texte
	fenetre.blit(text, (160,0))
	#affichage deuxième ligne de texte
	fenetre.blit(text1, (0,150))
	#affichage troisième ligne de texte
	fenetre.blit(text2, (0,200))
	#affichage quatrième ligne de texte
	fenetre.blit(text3, (0,300))
	pygame.display.flip()
# Création et affichage de la fenêtre de remerciement
def merci () :
	#création fenêtre de remerciement
	fenetre=pygame.display.set_mode((720,420),pygame.FULLSCREEN)
	#configuration font
	font=pygame.font.Font (None , 120)
	#configuration du texte
	text = font.render ("Merci",1, (255,255,255))
	#affichage du texte
	fenetre.blit (text,  (250,150))
	pygame.display.flip ()
	#Pause
	time.sleep (3)
bienvenue ()
if (os.path.isdir("/media/pi/PHOTO") == False): # si le dossier pour stocker les photos n'existe pas       
		os.mkdir("/media/pi/PHOTO")                  # alors on crée le dossier 
		os.chmod("/media/pi/PHOTO",0o777)
while True:
# Si commande via le GPIO décommenter la partie 1, si commande via le clavier décommenter la partie 2
#Partie 1
	# ecoute du GPIO2
	etat=GPIO.input (2)
	# ecoute du GPIO 3
	etat2=GPIO.input(3)
	if (etat==0):
		timer ()
		#montage du volume sur /media/pi/PHOTO
		os.system ("mount /dev/sda1 /media/pi/PHOTO")
		creationdossierdroit ()
		# prise de photo
		os.system("gphoto2 --capture-image-and-download --filename /media/pi/PHOTO/photos/droits/capt_%y_%m_%d-%H_%M_%S.jpg")
		merci ()
		# démonter le volume monter sur /media/pi/PHOTO
		os.system("umount -f /media/pi/PHOTO")				
		bienvenue ()
	if (etat2==0):
		timer ()
		# montage du volume sur /media/pi/PHOTO
		os.system ("mount /dev/sda1 /media/pi/PHOTO")
		creationdossierpasdroit ()
		#prise de photo
		os.system("gphoto2 --capture-image-and-download --filename /media/pi/PHOTO/photos/pasdroits/capt_%y_%m_%d-%H_%M_%S.jpg")
		merci()
		#démontage du volume monter sur /media/pi/PHOTO
		os.system("umount -f /media/pi/PHOTO")
		bienvenue ()
else:
#Partie 2
#	for event in pygame.event.get():    #Attente des événements
			

#			if event.type == KEYDOWN:

				#if event.key == K_a: #Si "a" est  préssé 
	#			
	#				timer ()
	#				creationdossierdroit ()
	#				#prise de photo
	#				os.system("gphoto2 --capture-image-and-download --filename /media/pi/PHOTO/photos/droits/capt_%y_%m_%d-%H_%M_%S.jpg")				
	#							
	#			if event.key == K_z: #Si "z" est préssé
	#				timer ()
	#				creationdossierpasdroit ()
					#prise de photo
	#				os.system("gphoto2 --capture-image-and-download --filename /media/pi/PHOTO/photos/pasdroits/capt_%y_%m_%d-%H_%M_%S.jpg")
				
			#	if event.key == K_e : #Si "e" est préssé
			#		#quitter les fenêtres
					pygame.quit ()
