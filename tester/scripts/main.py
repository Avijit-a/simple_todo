import http.server
import json
import logging


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Get the path of the requested resource
        path = self.path

        # If the path is "/", return a "Hello World!" message
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Hello World!')

        # If the path is not recognized, return a 404 error
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('Not found')


logging.error("RELOAD COMPLETE")
http = http.server.HTTPServer(("", 8888), MyHandler)
http.serve_forever()
