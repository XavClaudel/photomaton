# 📸 Photomaton DIY

Application de photomaton moderne, tactile et autonome, développée en Python (Tkinter, Pillow, OpenCV).  
Conçue initialement pour **Raspberry Pi** avec écran tactile, imprimante photo et bouton poussoir arcade, elle fonctionne également sous **Linux** et **macOS**.

---

## ✨ Fonctionnalités

- **Double caméra intelligente :**
  - Aperçu vidéo en direct et fluide via **Webcam** (OpenCV).
  - Prise de vue haute définition via un appareil photo **Reflex / DSLR** (`gphoto2`).
  - Repli automatique sur la webcam si aucun reflex n'est connecté.
- **Interface tactile plein écran :**
  - Design moderne, sombre et contrasté, adapté aux écrans tactiles.
  - Décompte visuel géant avant chaque prise de vue.
  - Système de notifications discrètes et non-bloquantes.
- **Modes de prise de vue :**
  - **Photo unique** avec décompte paramétrable.
  - **Mode Montage :** enchaînement de 4 photos au format **Grille 2x2** ou **Bandelette 1x4**.
  - **Galerie intégrée :** pour revoir les photos de l'événement et relancer une impression.
- **Retouche et personnalisation en direct :**
  - Effets cumulables : Noir & Blanc, Sépia, Vignettage, Netteté, Flou, Contour.
  - Incrustation de cadre personnalisé (fichier PNG avec transparence).
  - Marquage texte personnalisable (date, prénoms des mariés, nom de l'événement, choix de la police, de la taille, de la position et de la couleur).
- **Impression instantanée (CUPS) :**
  - Envoi direct vers l'imprimante photo (ex: Canon Selphy).
  - Ajustement automatique au ratio photo 3:2 (avec bandes `pad` ou rognage `crop`).
  - Quota d'impressions par photo paramétrable pour éviter le gaspillage de consommables.
- **Téléchargement sur smartphone via QR Code (Mode déconnecté) :**
  - Serveur web HTTP intégré servant les photos en direct.
  - Génération automatique d'un point d'accès Wi-Fi (**Hotspot**) via `nmcli` si aucune connexion réseau n'est présente sur le lieu de l'événement.
- **Sauvegarde amovible (USB) :**
  - Détection automatique des clés USB branchées.
  - Sauvegarde automatique en arrière-plan et/ou sauvegarde manuelle des photos personnalisées dans un sous-dossier daté (`Photomaton/AAAA-MM-JJ/`).
- **Déclencheur physique (GPIO) :**
  - Support natif d'un bouton poussoir arcade câblé sur le Raspberry Pi avec filtrage anti-rebond.

---

## 🛠️ Matériel Recommandé

- **Calculateur :** Raspberry Pi 4 ou 5 (recommandé : 2 Go de RAM ou plus).
- **Affichage :** Écran tactile officiel Raspberry Pi ou écran HDMI tactile.
- **Caméra :**
  - Un boîtier reflex numérique compatible `gphoto2` (Canon EOS, Nikon, Sony, etc.) relié en USB.
  - Une webcam USB grand angle pour le retour vidéo en direct.
- **Imprimante :** Imprimante photo compacte supportée par CUPS (ex: Canon SELPHY CP1300 / CP1500).
- **Déclencheur :** Bouton poussoir d'arcade connecté entre une broche GPIO (par défaut **BCM 2**) et la masse (**GND**). Voir les schémas dans le dossier `schéma/`.
- **Stockage :** Une clé USB formatée en FAT32/exFAT.

---

## 🚀 Démarrage Rapide

### 1. Utilisation du script automatisé (Recommandé)

Le script `launch.sh` s'occupe de tout : vérification des dépendances système, préparation du venv, configuration du point d'accès Wi-Fi en mode hors-ligne et lancement de l'application.

```bash
chmod +x launch.sh
./launch.sh
```

> **Note :** Si l'application doit créer un point d'accès Wi-Fi autonome ou installer des paquets système au premier lancement, des privilèges administrateur peuvent être demandés (`sudo ./launch.sh`).

### 2. Lancement manuel

Assurez-vous que les dépendances système sont installées :
```bash
sudo apt-get update
sudo apt-get install -y gphoto2 cups cups-client network-manager
```

Créez et activez votre environnement virtuel, puis installez les dépendances Python :
```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -U uv
uv pip sync pyproject.toml
```

Lancez l'application :
```bash
python main.py
```

---

## ⚙️ Configuration (`config.json`)

Le fichier `config.json` centralise les options du photomaton. Il est éditable à la main ou via **l'écran d'options** affiché au démarrage de l'application :

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `countdown_seconds` | `int` | `5` | Durée du décompte en secondes avant la capture |
| `enable_printing` | `bool` | `true` | Active ou désactive la fonction d'impression |
| `max_prints_per_photo` | `int` | `5` | Nombre maximal d'impressions autorisées par cliché |
| `printer_name` | `string|null` | `null` | Nom de l'imprimante CUPS (ou `null` pour la valeur par défaut système) |
| `print_fit_method` | `string` | `"pad"` | Méthode d'ajustement du format 3:2 : `"pad"` (bandes) ou `"crop"` (rogner) |
| `enable_usb_save` | `bool` | `true` | Sauvegarde automatique des photos sur clé USB |
| `enable_web_server` | `bool` | `false` | Active le serveur HTTP local et le QR Code |
| `hotspot_ssid` | `string` | `"photomaton"` | Nom du réseau Wi-Fi créé en mode hors-ligne |
| `hotspot_password` | `string` | `""` | Mot de passe du Wi-Fi (vide = réseau ouvert) |
| `enable_text_marking` | `bool` | `true` | Incruste un texte personnalisé sur les photos |
| `marking_text` | `string` | `""` | Contenu du texte (ex: "Mariage d'Alice & Bob") |
| `marking_text_font` | `string` | `"Lobster-Regular.ttf"` | Fichier de police situé dans le dossier `assets/` |
| `marking_text_size` | `int` | `80` | Taille de la police en pixels |
| `marking_text_color` | `string` | `"Blanc"` | Couleur du texte (`"Blanc"`, `"Noir"`, `"Rouge"`, `"Jaune"`) |
| `marking_text_position`| `string` | `"En bas à droite"` | Emplacement du texte sur l'image |
| `overlay_path` | `string` | `"assets/overlay.png"` | Chemin du cadre PNG transparent appliqué aux photos |
| `gpio_button_pin` | `int` | `2` | Numéro de broche BCM pour le bouton poussoir physique |

---

## 🎨 Personnalisation Graphique

- **Cadre photo personnalisé :**  
  Placez votre propre image au format PNG avec transparence à l'emplacement `assets/overlay.png`.
- **Nouvelles polices d'écriture :**  
  Déposez vos polices vectorielles (`.ttf`) dans le dossier `assets/` pour les rendre disponibles lors de la configuration du marquage.
- **Icônes :**  
  Les icônes de l'interface sont modifiables dans `assets/` (fichiers PNG optimisés, sources disponibles dans `assets/svg/`).

---

## 📁 Organisation du Répertoire

```text
├── assets/                 # Icônes, polices et cadre de superposition
├── photos/                 # Dossier généré contenant les clichés classés par jour (YYYY-MM-DD)
├── schéma/                 # Câblage Fritzing (.fzz et .pdf) pour le bouton GPIO
├── main.py                 # Interface Tkinter et orchestration
├── camera_manager.py       # Gestion du reflex (gphoto2) et de la webcam (OpenCV)
├── image_processor.py      # Filtres d'effets, marquage texte et montages (Pillow)
├── printer_manager.py      # Pilote d'impression CUPS
├── gpio_manager.py         # Gestionnaire matériel du bouton poussoir arcade
├── usb_manager.py          # Détection et transfert vers clé USB
├── web_server_manager.py   # Serveur HTTP local pour QR Code
├── ui_config_screen.py     # Écran de configuration initiale
├── ui_gallery_screen.py    # Écran de navigation galerie
├── launch.sh               # Script de lancement autonome
└── config.json             # Configuration de l'événement
```

---

## 📄 Licence & Crédits

- Projet développé par **Xavier Claudel**.
- Typographie `Lobster-Regular.ttf` sous licence SIL Open Font License (OFL).

