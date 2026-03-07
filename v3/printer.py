import cups

def print_photo(path):

    conn = cups.Connection()

    printers = conn.getPrinters()
    printer = list(printers.keys())[0]

    conn.printFile(printer, str(path), "Photomaton", {})