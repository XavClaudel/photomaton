#!/bin/bash

# Se déplacer dans le répertoire où se trouve le script
# C'est une bonne pratique pour s'assurer que tous les chemins relatifs (comme 'photos/' ou 'assets/') fonctionnent correctement.
cd "$(dirname "$0")"

# --- Vérification de la connexion Internet et installation des dépendances ---
echo "Vérification de la connexion Internet..."

# La commande 'ping -c 1 8.8.8.8' envoie un seul paquet au serveur DNS de Google.
# '&> /dev/null' masque la sortie de la commande pour un affichage plus propre.
if ping -c 1 8.8.8.8 &> /dev/null
then
    echo "Connexion Internet détectée. Préparation de l'environnement virtuel..."

    # --- Installation automatique des paquets système manquants ---
    MISSING_APT=""
    if ! command -v gphoto2 &> /dev/null; then
        MISSING_APT="$MISSING_APT gphoto2"
    fi
    
    if [ -f /proc/device-tree/model ] && grep -q -i "Raspberry Pi" /proc/device-tree/model; then
        if ! dpkg -s python3-gpiozero &> /dev/null; then MISSING_APT="$MISSING_APT python3-gpiozero"; fi
        if ! dpkg -s python3-lgpio &> /dev/null; then MISSING_APT="$MISSING_APT python3-lgpio"; fi
    fi

    if [ -n "$MISSING_APT" ]; then
        echo "Installation des dépendances système requises ($MISSING_APT)..."
        echo "Votre mot de passe administrateur (sudo) peut être demandé."
        sudo apt-get update
        sudo apt-get install -y $MISSING_APT
    fi

    # Crée l'environnement virtuel '.venv' si le dossier n'existe pas.
    if [ ! -d ".venv" ]; then
        echo "Environnement virtuel non trouvé. Création en cours..."
        python3 -m venv --system-site-packages .venv
        if [ $? -ne 0 ]; then
            echo "ERREUR: La création de l'environnement virtuel a échoué."
            exit 1
        fi
    else
        # Force l'accès aux paquets système (comme gpiozero installé via apt) pour un venv existant
        if [ -f ".venv/pyvenv.cfg" ]; then
            sed -i 's/include-system-site-packages = false/include-system-site-packages = true/g' .venv/pyvenv.cfg
        fi
    fi

    # Active l'environnement virtuel pour la session du script.
    source .venv/bin/activate

    # Installe 'uv' à l'intérieur de l'environnement virtuel, évitant les conflits système.
    echo "Installation/Mise à jour de 'uv' dans l'environnement local..."
    pip install -U uv

    echo "Synchronisation des dépendances avec 'uv'..."
    uv pip sync pyproject.toml

else
    echo "AVERTISSEMENT : Pas de connexion Internet."
    # Vérifie s'il y a une connexion réseau local (une IP non-loopback)
    if ip addr | grep -q "inet .*global"; then
        echo "Une connexion réseau local a été détectée. Lancement avec les dépendances locales."
    else
        echo "Aucune connexion réseau local détectée. Tentative de création d'un point d'accès Wi-Fi..."
        
        # On délègue à network_manager.py (même logique que l'application) :
        # - réutilise le profil hotspot existant s'il y en a un (l'imprimante retrouve le même réseau),
        # - crée un vrai réseau OUVERT si le mot de passe est vide
        #   ('nmcli dev wifi hotspot' sans mot de passe en génère un aléatoire),
        # - enregistre l'IP du hotspot dans config.json pour le QR code.
        python3 - <<'EOF'
import json, os
import network_manager

cfg_path = 'config.json'
config = {}
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        config = json.load(f)
ssid = config.get('hotspot_ssid', 'photomaton')
password = config.get('hotspot_password', 'photobooth')

success, ip, message = network_manager.start_hotspot(ssid, password)
if not success:
    print(f"ERREUR: {message}")
    print("Cela peut être dû à un manque de permissions (essayez avec 'sudo').")
else:
    print(message)
    if password:
        print(f"Connectez votre téléphone au Wi-Fi '{ssid}' (mot de passe: '{password}').")
    else:
        print(f"Connectez votre téléphone au Wi-Fi ouvert '{ssid}'.")
    if ip:
        config['web_server_ip'] = ip
        with open(cfg_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Le photomaton est accessible à l'adresse IP : {ip} (configurée pour le QR Code).")
EOF
    fi
    source .venv/bin/activate
fi

# --- Lancement de l'application Python ---
echo "Lancement du Photomaton..."
python main.py

echo "Fermeture de l'application."
deactivate