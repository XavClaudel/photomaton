#!/usr/bin/env bash
set -e  # stoppe en cas d'erreur

# Vérifie que poetry est installé
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry n'est pas installé. Installe-le d'abord : https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "📦 Installation des dépendances avec Poetry..."
poetry install

echo "🚀 Lancement de l'application Flask..."
poetry run python scrpit_photomation_raspberry.py