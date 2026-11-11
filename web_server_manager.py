import http.server
import socketserver
import socket
import os

def start_server(directory: str = '.', port: int = 8000) -> None:
    """
    Lance un simple serveur HTTP pour servir les fichiers d'un répertoire.
    Il est destiné à être lancé dans un thread séparé pour ne pas bloquer l'interface.
    """
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serveur web démarré sur http://0.0.0.0:{port}, servant le dossier '{directory}'")
        httpd.serve_forever()

def get_local_ip() -> str:
    """Récupère l'adresse IP locale de la machine sur le réseau."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1)) # IP non routable, ne génère pas de trafic
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1' # Si la connexion échoue, retourne l'IP locale
    finally:
        s.close()
    return IP