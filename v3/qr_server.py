from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

def start_server(port, directory):

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    server = HTTPServer(("", port), Handler)

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    return server