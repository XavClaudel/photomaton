from pathlib import Path

import cups

import os
import time
from config import *
import pygame

from ui import  draw_print_screen


def impression_photo(screen :pygame.Surface,font,path: str | Path, printer_name: str | None = None, timeout: int = 60) -> int:
    """
    Envoie une image à l'imprimante via CUPS et attend la fin du job.

    Args:
        path: chemin de l'image
        printer_name: imprimante à utiliser (None = défaut)
        timeout: temps max d'attente en secondes

    Returns:
        job_id
    """

    path = str(path)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Le fichier {path} n'existe pas")

    conn = cups.Connection()

    printers = conn.getPrinters()

    if not printers:
        raise RuntimeError("Aucune imprimante détectée")

    # choisir imprimante
    if printer_name is None:
        printer_name = conn.getDefault()

        if printer_name is None:
            printer_name = list(printers.keys())[0]

    if printer_name not in printers:
        raise RuntimeError(f"Imprimante '{printer_name}' introuvable")
    from PIL import Image


    print(f"Impression sur : {printer_name}")
    print(f"Fichier : {path}")

    # options impression
    options = {
        "media": "Postcard.Fullbleed",
        "fit-to-page": "True",
        "print-quality": "5",
        "ColorModel": "RGB",
        "Resolution": "300dpi"
    }

    job_id = conn.printFile(
        printer_name,
        path,
        "Photomaton Print",
        options
    )

    print(f"Job envoyé : {job_id}")
    draw_print_screen(screen=screen,font_small=font)
    # attendre la fin du job
    start = time.time()

    while True:

        jobs = conn.getJobs()

        if job_id not in jobs:
            print("Impression terminée")
            break

        if time.time() - start > timeout:
            raise TimeoutError("Timeout impression")

        time.sleep(2)

    return job_id


def printer_status(printer):

    conn = cups.Connection()
    printers = conn.getPrinters()

    if printer not in printers:
        return "unknown"

    state = printers[printer]["printer-state"]

    states = {
        3: "idle",
        4: "printing",
        5: "stopped"
    }

    return states.get(state, "unknown")