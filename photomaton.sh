#!/usr/bin/env bash
set -e

echo "🚀 Initialisation du photomaton"

############################################
# Vérification connexion internet
############################################

has_internet() {
    ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1
}

INTERNET=false
if has_internet; then
    INTERNET=true
    echo "🌐 Internet disponible"
else
    echo "⚠️ Pas de connexion internet"
fi

############################################
# Détection gestionnaire de paquets
############################################

PKG_MANAGER=""

if command -v apt &> /dev/null; then
    PKG_MANAGER="apt"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
fi

############################################
# Mise à jour des dépôts (une seule fois)
############################################

if [ "$INTERNET" = true ] && [ "$PKG_MANAGER" = "apt" ]; then
    echo "📦 Mise à jour des dépôts"
    sudo apt update
fi

############################################
# Fonction installation package
############################################

install_package() {

    PACKAGE=$1
    COMMAND=$2

    if ! command -v "$COMMAND" &> /dev/null; then

        echo "📦 $PACKAGE non trouvé"

        if [ "$INTERNET" = false ]; then
            echo "⚠️ Impossible d'installer $PACKAGE sans internet"
            return
        fi

        echo "⬇️ Installation de $PACKAGE..."

        if [ "$PKG_MANAGER" = "apt" ]; then
            sudo apt install -y "$PACKAGE"
        elif [ "$PKG_MANAGER" = "dnf" ]; then
            sudo dnf install -y "$PACKAGE"
        else
            echo "⚠️ Gestionnaire de paquet non supporté"
            exit 1
        fi

    else
        echo "✅ $PACKAGE déjà installé"
    fi
}

############################################
# Installation dépendances système
############################################

install_package "gphoto2" "gphoto2"
install_package "pmount" "pmount"
install_package "libcups2-dev" "lp"
install_package "python3-dev" "libcups2-dev" "gcc"
install_package "python3-cups"

############################################
# Création environnement virtuel
############################################

if [ ! -d ".venv" ]; then
    echo "🐍 Création environnement virtuel"
    python3 -m venv .venv
fi

source .venv/bin/activate

############################################
# Installation outils python
############################################

if [ "$INTERNET" = true ]; then

    echo "📦 Mise à jour pip"
    pip install --upgrade pip setuptools wheel

    echo "🧹 Nettoyage cups"
    pip uninstall -y cups || true

    if ! command -v poetry &> /dev/null; then
        echo "🚀 Installation Poetry"
        pip install poetry
    else
        echo "✅ Poetry déjà installé"
    fi

    echo "📦 Installation dépendances Python"
    poetry lock
    poetry install

else
    echo "⚠️ Installation Python ignorée (pas d'internet)"
fi

############################################
# Lancement photomaton
############################################

echo "🎬 Lancement du photomaton..."

poetry run python main.py