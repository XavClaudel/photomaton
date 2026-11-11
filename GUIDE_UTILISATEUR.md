# Photomaton - Guide d'Utilisation

Bienvenue dans le guide d'utilisation de votre application Photomaton ! Ce document vous explique comment lancer, configurer et utiliser toutes les fonctionnalités de l'application.

## 1. Lancement de l'Application

Pour démarrer, exécutez simplement le script `launch.sh` dans votre terminal :

```bash
./launch.sh
```

Ce script intelligent s'occupe de tout :
- Il vérifie si les dépendances logicielles sont installées et les installe si nécessaire (nécessite une connexion Internet au premier lancement).
- Si aucune connexion réseau n'est détectée, il peut **créer son propre point d'accès Wi-Fi** pour que les invités puissent télécharger leurs photos.

> **Note :** La création du point d'accès peut nécessiter des droits d'administrateur. Si cela échoue, essayez de lancer le script avec `sudo ./launch.sh`.

## 2. Écran de Configuration

Au lancement, un écran de configuration vous permet d'activer ou de désactiver les fonctionnalités principales pour votre événement.

- **Activer l'impression :** Permet d'imprimer les photos. Assurez-vous qu'une imprimante est connectée et configurée.
- **Activer la sauvegarde sur USB :** Permet de sauvegarder les photos sur une clé USB. Une clé doit être branchée pour activer cette option.
- **Activer le QR Code de téléchargement :** Affiche un QR code sur l'écran de prévisualisation pour permettre aux invités de télécharger leur photo sur leur smartphone.
- **Personnalisation des photos :** Active le panneau d'effets (Noir & Blanc, Sépia, etc.) sur l'écran de prévisualisation.
- **Marquage photo :** Permet d'incruster un texte personnalisé sur chaque photo.
    - **Champ de texte :** Saisissez le texte à afficher (ex: "Mariage de A & B").
    - **Options :** Vous pouvez choisir la police, la taille, la couleur et la position du texte.

Une fois vos options choisies, cliquez sur **"Lancer le Photomaton"**.

## 3. Utilisation du Photomaton

### Écran d'Accueil

Vous avez deux choix :
- **Prendre une photo :** Lance le décompte pour une seule photo.
- **Mode Montage :** Ouvre une fenêtre pour choisir entre un format "Grille 2x2" ou "Bande 1x4", puis lance la séquence de 4 photos.
- **Galerie :** Ouvre un écran pour voir et ré-imprimer les photos déjà prises.

### Décompte

Un décompte s'affiche à l'écran avant chaque prise, laissant le temps aux invités de prendre la pose.

## 4. Écran de Prévisualisation

Après la prise de vue, la photo s'affiche. Vous pouvez alors :

- **Reprendre :** Annule la photo actuelle et retourne à l'écran d'accueil.
- **Imprimer :** Envoie la photo (avec ses effets) à l'imprimante. Le nombre d'impressions par photo peut être limité.
- **Effets :** Ouvre un panneau latéral pour personnaliser votre photo.

### Panneau d'Effets

Cliquez sur le bouton "Effets" pour faire apparaître le panneau. Les effets sont cumulables !
- **Noir & Blanc / Sépia :** Filtres de couleur classiques.
- **Vignette :** Assombrit les bords de la photo.
- **Netteté / Flou :** Accentue ou adoucit les détails.
- **Contour :** Donne un effet "dessin".
- **Cadre :** Applique une image de cadre (voir personnalisation).
- **Reset :** Annule tous les effets appliqués.

### Téléchargement par QR Code

Si l'option est activée, un QR code apparaît en bas à droite. Pour l'utiliser :
1.  Connectez votre smartphone au même réseau Wi-Fi que le photomaton.
2.  Scannez le code avec l'appareil photo de votre téléphone.
3.  Un lien apparaîtra pour télécharger l'image.

## 5. Fonctionnalités Avancées

### Mode Point d'Accès (Hotspot)

Si le photomaton est lancé dans un lieu sans Wi-Fi, il créera son propre réseau.
- **Nom du réseau (SSID) par défaut :** `photomaton`
- **Mot de passe par défaut :** `photobooth` (peut être laissé vide pour un réseau ouvert)

Les invités n'ont qu'à se connecter à ce réseau pour utiliser le QR code.

### Bouton Physique (pour Raspberry Pi)

Si vous utilisez un Raspberry Pi, vous pouvez brancher un bouton physique sur les broches GPIO pour déclencher la prise de photo sans toucher à l'écran.

## 6. Personnalisation (pour l'organisateur)

Vous pouvez personnaliser certains aspects en modifiant des fichiers avant de lancer l'application.

- **Fichier de configuration (`config.json`) :** Ce fichier centralise de nombreuses options. Vous pouvez y changer le texte par défaut du marquage, le nom/mot de passe du hotspot, etc.
- **Cadre personnalisé :** Remplacez l'image `assets/overlay.png` par votre propre fichier PNG (avec transparence) pour avoir un cadre personnalisé.
- **Polices personnalisées :** Ajoutez des fichiers de police (`.ttf`) dans le dossier `assets/` pour qu'ils apparaissent dans les options de marquage.