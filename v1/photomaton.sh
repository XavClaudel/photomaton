#!/usr/bin/env bash
set -e

# Vérifie si gphoto2 est installé (binaire système)
if ! command -v gphoto2 &> /dev/null; then
    echo "📸 gphoto2 non trouvé, installation..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y gphoto2
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y gphoto2
    else
        echo "⚠️ Impossible de détecter un gestionnaire de paquets compatible. Installe gphoto2 manuellement."
        exit 1
    fi
else
    echo "✅ gphoto2 déjà installé"
fi


# Vérifie si pmount est installé (binaire système)
if ! command -v pmount &> /dev/null; then
    echo "📸 pmount non trouvé, installation..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y pmount
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y pmount
    else
        echo "⚠️ Impossible de détecter un gestionnaire de paquets compatible. Installe pmount manuellement."
        exit 1
    fi
else
    echo "✅ pmount déjà installé"
fi

# Vérifie si libcups2-dev est installé (binaire système)
if ! command -v libcups2-dev &> /dev/null; then
    echo "📸 libcups2-dev non trouvé, installation..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y libcups2-dev
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y libcups2-dev
    else
        echo "⚠️ Impossible de détecter un gestionnaire de paquets compatible. Installe pmount manuellement."
        exit 1
    fi
else
    echo "✅ pmount déjà installé"
fi

# Crée un venv local si pas déjà présent
if [ ! -d ".venv" ]; then
    echo "📦 Création d'un environnement virtuel local..."
    python3 -m venv .venv

fi

# Active le venv
source .venv/bin/activate

# Vérifie si pip est dispo
pip install --upgrade pip setuptools wheel
pip uninstall cups
# Vérifie si poetry est installé dans ce venv
if ! command -v poetry &> /dev/null; then
    echo "🚀 Installation de Poetry dans le venv..."
    pip install poetry
fi

echo "📦 Installation des dépendances avec Poetry..."
poetry lock
poetry install




echo "🚀 Lancement du photomaton..."
poetry run python scrpit_photomation_raspberry.py
