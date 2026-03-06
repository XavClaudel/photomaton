#!/usr/bin/env bash
set -e  # stoppe en cas d'erreur
echo "📦 Installation de gphoto2..."
# Vérifie que poetry est installé
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry n'est pas installé. Installe-le d'abord : https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "📦 Installation des dépendances avec Poetry..."
poetry install
# Vérifie si gphoto2 est installé
if ! command -v gphoto2 &> /dev/null; then
    echo "📸 gphoto2 non trouvé, installation..."
    
    # Détection OS simple (Ubuntu/Debian)
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y gphoto2
    elif command -v dnf &> /dev/null; then
        sudo dnf install gphoto2
    else
        echo "⚠️ Impossible de détecter un gestionnaire de paquets compatible. Installe gphoto2 manuellement."
        exit 1
    fi
else
    echo "✅ gphoto2 déjà installé"
fi

echo "🚀 Lancement de l'application Flask..."
poetry run python app.py