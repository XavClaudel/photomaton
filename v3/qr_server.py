from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import threading
import os


def start_server(folder, port):

    os.chdir(folder)

    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(("", port), handler)

    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()

    return httpd