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
        
        if command -v nmcli &> /dev/null; then
            WIFI_IFACE=$(nmcli -t -f DEVICE,TYPE dev | grep ':wifi$' | cut -d':' -f1 | head -n 1)
            if [ -n "$WIFI_IFACE" ]; then
                echo "Interface Wi-Fi trouvée : $WIFI_IFACE"
                
                # Lecture de la configuration du hotspot depuis config.json avec Python, ou valeurs par défaut
                if [ -f "config.json" ]; then
                    # On lit les deux valeurs en une seule fois pour être plus efficace
                    CONFIG_VALUES=$(python3 -c "import json; c=json.load(open('config.json')); print(c.get('hotspot_ssid', 'photomaton')); print(c.get('hotspot_password', 'photobooth'))")
                    SSID=$(echo "$CONFIG_VALUES" | head -n 1)
                    PASSWORD=$(echo "$CONFIG_VALUES" | tail -n 1)
                else
                    SSID="photomaton"
                    PASSWORD="photobooth"
                fi

                # On vérifie si un mot de passe a été fourni
                if [ -n "$PASSWORD" ]; then
                    echo "Création du hotspot sécurisé '$SSID'. Si cela échoue, essayez de lancer ce script avec 'sudo'."
                    # Tente de créer le hotspot sécurisé. Peut nécessiter des droits admin.
                    nmcli dev wifi hotspot ifname "$WIFI_IFACE" ssid "$SSID" password "$PASSWORD"
                else
                    echo "Création du hotspot ouvert '$SSID' (sans mot de passe). Si cela échoue, essayez de lancer ce script avec 'sudo'."
                    # Tente de créer le hotspot ouvert.
                    nmcli dev wifi hotspot ifname "$WIFI_IFACE" ssid "$SSID"
                fi

                if [ $? -eq 0 ]; then
                    echo "Point d'accès '$SSID' créé avec succès."
                    # Affiche le message approprié avec ou sans mot de passe
                    [ -n "$PASSWORD" ] && echo "Connectez votre téléphone au Wi-Fi '$SSID' (mot de passe: '$PASSWORD')." || echo "Connectez votre téléphone au Wi-Fi ouvert '$SSID'."
                    sleep 5 # Laisse le temps au réseau de s'établir

                    # Récupère l'IP du point d'accès et la force dans la configuration
                    # La sortie est du type "IP4.ADDRESS[1]:192.168.4.1/24", on doit extraire juste l'IP.
                    HOTSPOT_IP=$(nmcli -t -f IP4.ADDRESS dev show "$WIFI_IFACE" | cut -d':' -f2 | cut -d'/' -f1 | head -n 1)
                    if [ -n "$HOTSPOT_IP" ]; then
                        echo "Le photomaton est accessible à l'adresse IP : $HOTSPOT_IP"
                        python3 -c "import json, os; cfg_path='config.json'; data={} if not os.path.exists(cfg_path) else json.load(open(cfg_path)); data['web_server_ip']='$HOTSPOT_IP'; json.dump(data, open(cfg_path, 'w'), indent=4);"
                        echo "L'adresse IP a été configurée pour le QR Code."
                    fi
                else
                    echo "ERREUR: La création du point d'accès a échoué. Cela peut être dû à un manque de permissions (essayez avec 'sudo')."
                fi
            else
                echo "AVERTISSEMENT: Aucune interface Wi-Fi n'a été trouvée pour créer un point d'accès."
            fi
        else
            echo "AVERTISSEMENT: 'nmcli' (NetworkManager) n'est pas installé. Impossible de créer un point d'accès automatiquement."
        fi
    fi
    source .venv/bin/activate
fi

# --- Lancement de l'application Python ---
echo "Lancement du Photomaton..."
python main.py

echo "Fermeture de l'application."
deactivate