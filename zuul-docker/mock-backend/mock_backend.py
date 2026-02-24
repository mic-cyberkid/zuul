from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.log_request_details()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Backend Response: OK")

    def do_POST(self):
        self.log_request_details()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Backend Response: POST OK")

    def log_request_details(self):
        print("\n" + "="*40)
        print(f"RECEIVED REQUEST: {self.command} {self.path}")
        print("HEADERS:")
        for k, v in self.headers.items():
            print(f"  {k}: {v}")
        print("="*40 + "\n")

if __name__ == "__main__":
    port = 8080
    print(f"Mock Backend starting on port {port}...")
    httpd = HTTPServer(('0.0.0.0', port), MockHandler)
    httpd.serve_forever()
