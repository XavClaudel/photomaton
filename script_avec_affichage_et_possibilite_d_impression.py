#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import time
import os
import sys
import RPi.GPIO as GPIO, time
#déclaration des ports GPIO que l'on utilise
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN )
GPIO.setup(3, GPIO.IN)
def timer () :
	#Création de la fenêtre 5
	fenetre = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/5.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (640, 480)), (0, 0))
	pygame.display.flip()
	#Pause
	time.sleep (1)
	#Création de la fenêtre 4
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/4.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (640, 480)), (0, 0))
	pygame.display.flip()
	#Pause
	time.sleep (1)
	#Création de la fenêtre 3
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/3.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (640, 480)), (0, 0))
	pygame.display.flip()
	#Pause
	time.sleep (1)
	#Création de la fenêtre 2
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/2.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (640, 480)), (0, 0))
	pygame.display.flip()
	time.sleep (1)
	#Création de la fenêtre 1
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/1.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (640, 480)), (0, 0))
	pygame.display.flip()
	#Pause
	time.sleep (1)
	#Création de la fenêtre 0
	decompte = pygame.image.load("/home/pi/Documents/photomaton/images/0.jpg").convert()
	fenetre.blit(pygame.transform.scale(decompte, (640, 480)), (0, 0))
	pygame.display.flip()
		 
def creationdossierdroit () :
	if (os.path.isdir("/media/pi/PHOTO/photos") == False): # si le dossier pour stocker les photos n'existe pas       
		os.mkdir("/media/pi/PHOTO/photos")                  # alors on crée le dossier *
		print("creation ok")
		os.chmod("/media/pi/PHOTO/photos",0o777)            # et on change les droits pour pouvoir effacer des photos
	if (os.path.isdir("/media/pi/PHOTO/photos/droits") == False): # si le dossier pour stocker les photos n'existe pas       
		os.mkdir("/media/pi/PHOTO/photos/droits")                  # alors on crée le dossier 
		print("creation ok")
		os.chmod("/media/pi/PHOTO/photos/droits",0o777)            # et on change les droits pour pouvoir effacer des photos
	
def creationdossierpasdroit () :
	if (os.path.isdir("/media/pi/PHOTO/photos") == False): # si le dossier pour stocker les photos n'existe pas       
		os.mkdir("/media/pi/PHOTO/photos")                  # alors on crée le dossier 
		print("creation ok")
		os.chmod("/media/pi/PHOTO/photos",0o777)            # et on change les droits pour pouvoir effacer des photos
	if (os.path.isdir("//media/pi/PHOTO/photos/pasdroits") == False): # si le dossier pour stocker les photos n'existe pas       
		os.mkdir("/media/pi/PHOTO/photos/pasdroits")                  # alors on crée le dossier 
		print("creation ok")
		os.chmod("/media/pi/PHOTO/photos/pasdroits",0o777)            # et on change les droits pour pouvoir effacer des photos
		print("creation ok")
def creationtemp ():
	if (os.path.isdir("/home/pi/Documents/photomaton/tmp") == False): # si le dossier temporaire n'existe pas       
		os.mkdir("/home/pi/Documents/photomaton/tmp")                  # alors on crée le dossier 
		os.chmod("/home/pi/Documents/photomaton/tmp",0o777)            # et on change les droits pour pouvoir effacer des photos

#Initialisation de la bibliothèque Pygame
pygame.init()
#Création et affichage de la fenêtre bienvenue
def bienvenue () :
	fenetre = pygame.display.set_mode((640, 480),pygame.FULLSCREEN)
	font=pygame.font.Font(None, 120)
	font1=pygame.font.Font(None,50)
	text = font.render("Bienvenue",1,(255,255,255))
	text1 = font1.render(u"Appuyer sur le bouton vert",1, (255,255,255))
	text2 = font1.render(u"pour céder votre droits à l'image",1, (255,255,255))
	text3 = font1.render(u"Sinon appuyer sur le bouton rouge",1, (255,255,255))
	fenetre.blit(text, (140,0))
	fenetre.blit(text1, (15,150))
	fenetre.blit(text2, (15,200))
	fenetre.blit(text3, (15,300))
	pygame.display.flip()
# Création et affichage de la fenêtre de remerciement
def merci () :
	fenetre=pygame.display.set_mode((640,480),pygame.FULLSCREEN)
	font=pygame.font.Font (None , 120)
	text = font.render ("Merci",1, (255,255,255))
	fenetre.blit (text,  (230,200))
	pygame.display.flip ()
	os.system("lprm all")
	time.sleep (1)
# fonction d'affichage
def impression () :
	#print ("ok")
	os.system("lp /home/pi/Documents/photomaton/tmp/1.jpg")
	time.sleep (55)
	merci()
def affichage () :
	#affichage de l'image
	fenetre = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
	affichage = pygame.image.load("/home/pi/Documents/photomaton/tmp/1.jpg").convert()
	bouton_vert=pygame.image.load("/home/pi/Documents/photomaton/images/bouton_vert.png")
	bouton_rouge=pygame.image.load ("/home/pi/Documents/photomaton/images/bouton_rouge.png")
	font=pygame.font.Font(None, 22)
	text = font.render("Imprimer",1,(0,0,0))
	text1=font.render("Reprendre ",1, (0,0,0))
	text2=font.render("une photo",1,(0,0,0))
	fenetre.blit(pygame.transform.scale(affichage, (640, 480)), (0, 0))
	fenetre.blit(pygame.transform.scale(bouton_vert, (60,60)),(30,420))
	fenetre.blit(pygame.transform.scale(bouton_rouge, (60,60)),(470,420))
	fenetre.blit(text, (100,440))
	fenetre.blit(text1, (540,430))
	fenetre.blit(text2,(540,450))
	pygame.display.flip()
	repeat = True
	while repeat == True:
		#	 ecoute du GPIO2
		etat=GPIO.input (2)
		#	 ecoute du GPIO 3
		etat2=GPIO.input(3)
	
		if (etat==0):
			impression ()
			repeat = False
			bienvenue()
			break
		if (etat2==0):
			repeat= False
			time.sleep (1)
			bienvenue ()
			break
bienvenue ()
while True:
# Si commande via le GPIO décommenter la partie 1, si commande via le clavier décommenter la partie 2
#Partie 1
#	 ecoute du GPIO2
	etat=GPIO.input (2)
#	 ecoute du GPIO 3
	etat2=GPIO.input(3)
	
	if (etat==0):
		os.system ("rm -r /home/pi/Documents/photomaton/tmp")
		timer ()
		#montage de la clé
		os.system ("mount /dev/sda1 /media/pi/PHOTO")
		#on créer le dossier droit
		creationdossierdroit ()
		#création du fichier temporaire
		creationtemp()
		# prise de photo
		os.system("gphoto2 --capture-image-and-download --filename /home/pi/Documents/photomaton/tmp/capt_%y_%m_%d-%H_%M_%S.jpg")
		#os.system("fswebcam -v -i 0 -d v4l2:/dev/video0 -r 1280x720 -S 60 --jpeg 100 --save /home/pi/Documents/photomaton/tmp/timelapse-%Y-%m-%d--%H-%M-%S.jpg")
		#copie de la photo sur la clès usb
		os.system("cp /home/pi/Documents/photomaton/tmp/*jpg /media/pi/PHOTO/photos/droits")
		#on renomme la photo
		os.system("mv /home/pi/Documents/photomaton/tmp/*jpg /home/pi/Documents/photomaton/tmp/1.jpg")
		#on affiche la photo
		affichage()
		#démontage de la clé
		os.system ("umount /media/pi/PHOTO")
		#on supprime le dossier temporaire
		os.system("rm /home/pi/Documents/photomaton/tmp/1.jpg")
		bienvenue ()		
	if (etat2==0):
		os.system ("rm -r /home/pi/Documents/photomaton/tmp")
		timer ()
		#montage de la clés
		os.system ("mount /dev/sda1 /media/pi/PHOTO")
		#création du fichier pas droits
		creationdossierpasdroit ()
		#création du fichier temporaire
		creationtemp ()
		#prise de photo
		os.system("gphoto2 --capture-image-and-download --filename /home/pi/Documents/photomaton/tmp/capt_%y_%m_%d-%H_%M_%S.jpg")
		#os.system("fswebcam -v -i 0 -d v4l2:/dev/video0 -r 1280x720 -S 60 --jpeg 100 --save /home/pi/Documents/photomaton/tmp/timelapse-%Y-%m-%d--%H-%M-%S.jpg")
		# on copie la photo sur la clès usb
		os.system("cp /home/pi/Documents/photomaton/tmp/*jpg /media/pi/PHOTO/photos/pasdroits")
		#on renomme la photo
		os.system("mv /home/pi/Documents/photomaton/tmp/*jpg /home/pi/Documents/photomaton/tmp/1.jpg")
		#on affiche la photo
		affichage()
		#démontage de la clé
		os.system ("umount /media/pi/PHOTO")
		#on supprime le dossier temporaire
		os.system("rm /home/pi/Documents/photomaton/tmp/1.jpg")
		bienvenue ()
#else:
#Partie 2
	#for event in pygame.event.get():    #Attente des événements
			

	#		if event.type == KEYDOWN:

	#			if event.key == K_a: #Si "a" est  préssé 
	#				os.system ("rm -r /home/pi/Documents/photomaton/tmp")
	#				timer ()
					#montage de la clé
			#		os.system ("mount /dev/sda1 /media/pi/PHOTO")
					#on créer le dossier droit
	#				creationdossierdroit ()
					#création du fichier temporaire
	#				creationtemp()
					# prise de photo
	#				os.system("gphoto2 --capture-image-and-download --filename /home/pi/Documents/photomaton/tmp/capt_%y_%m_%d-%H_%M_%S.jpg")
					#os.system("fswebcam -v -i 0 -d v4l2:/dev/video0 -r 1280x720 -S 60 --jpeg 100 --save /home/pi/Documents/photomaton/tmp/timelapse-%Y-%m-%d--%H-%M-%S.jpg")
					#copie de la photo sur la clès usb
	#				os.system("cp /home/pi/Documents/photomaton/tmp/*jpg /home/pi/Documents/photomaton/photos/droits")
					#on renomme la photo
	#				os.system("mv /home/pi/Documents/photomaton/tmp/*jpg /home/pi/Documents/photomaton/tmp/1.jpg")
					#on affiche la photo
	#				affichage()
					#démontage de la clé
					#os.system ("umount /media/pi/PHOTO")
					#on supprime le dossier temporaire
	#				os.system("rm /home/pi/Documents/photomaton/tmp/1.jpg")
	#				bienvenue ()
								
	#			if event.key == K_z: #Si "z" est préssé
	#				os.system ("rm -r /home/pi/Documents/photomaton/tmp")
	#				timer ()
					#montage de la clés
					#os.system ("mount /dev/sda1 /media/pi/PHOTO")
					#création du fichier pas droits
	#				creationdossierpasdroit ()
					#création du fichier temporaire
	#				creationtemp ()
					#prise de photo
	#				os.system("gphoto2 --capture-image-and-download --filename /home/pi/Documents/photomaton/tmp/capt_%y_%m_%d-%H_%M_%S.jpg")
					#os.system("fswebcam -v -i 0 -d v4l2:/dev/video0 -r 1280x720 -S 60 --jpeg 100 --save /home/pi/Documents/photomaton/tmp/timelapse-%Y-%m-%d--%H-%M-%S.jpg")
					# on copie la photo sur la clès usb
	#				os.system("cp /home/pi/Documents/photomaton/tmp/*jpg /home/pi/Documents/photomaton/photos/pasdroits")
					#on renomme la photo
	#				os.system("mv /home/pi/Documents/photomaton/tmp/*jpg /home/pi/Documents/photomaton/tmp/1.jpg")
					#on affiche la photo
	#				affichage()
					#démontage de la clé
					#os.system ("umount /media/pi/PHOTO")
					#on supprime le dossier temporaire
	#				os.system("rm /home/pi/Documents/photomaton/tmp/1.jpg")
	#				bienvenue ()
	#			if event.key == K_e : #Si "e" est préssé
					#quitter les fenêtres
	#				pygame.quit ()
