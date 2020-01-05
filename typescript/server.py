import http.server
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import sys

port = 8080 if len(sys.argv) < 2 else int(sys.argv[1])

Handler = http.server.SimpleHTTPRequestHandler

Handler.extensions_map={
    '.manifest': 'text/cache-manifest',
    '.html': 'text/html',
    '.css':'text/css',
    '.js':'application/x-javascript',
    '': 'application/octet-stream', # Default
}

httpd = socketserver.TCPServer(("", port), Handler)

print(f"serving at http://0.0.0.0:{port}/static/index.html")
httpd.serve_forever()
