from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"Hello from backend on port {self.server.server_port}\n".encode())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python backend.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    httpd = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Starting backend on port {port}")
    httpd.serve_forever()
