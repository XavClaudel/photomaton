import cups

import cups
import os


def print_picture(path: str, printer_name: str | None = None) -> int:
    """
    Envoie une image à l'imprimante via CUPS.

    Args:
        path: chemin de l'image
        printer_name: imprimante à utiliser (None = défaut)

    Returns:
        job_id
    """

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

    print(f"Impression sur : {printer_name}")
    print(f"Fichier : {path}")

    options = {
        "fit-to-page": "True"
    }

    job_id = conn.printFile(
        printer_name,
        path,
        "Photomaton Print",
        options
    )

    print(f"Job envoyé : {job_id}")

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