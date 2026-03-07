import cups
import os

def print_picture(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    conn = cups.Connection()
    printers = conn.getPrinters()

    if not printers:
        raise RuntimeError("Aucune imprimante")

    printer = list(printers.keys())[0]

    conn.printFile(printer, path, "Photo", {})