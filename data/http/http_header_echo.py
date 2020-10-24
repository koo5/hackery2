from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import logging

PORT = 1234

class GetHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.error(self.headers)
        SimpleHTTPRequestHandler.do_GET(self)


Handler = GetHandler
httpd = TCPServer(("", PORT), Handler)

httpd.serve_forever()
