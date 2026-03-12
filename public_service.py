from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os

class MonolithHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"\n[BACKEND 8080] Received Request: {self.path}")

        # Simulate backend normalization bypass
        # Real backends like Tomcat/Spring might decode and normalize before matching routes
        decoded_path = urllib.parse.unquote(self.path)
        normalized_path = os.path.normpath(decoded_path).replace("\\", "/") # handle windows-style normpath

        print(f"[BACKEND 8080] Decoded: {decoded_path}, Normalized: {normalized_path}")

        if normalized_path.startswith("/admin/secrets"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"CONFIDENTIAL DATA: The cake is a lie.")
        elif normalized_path.startswith("/admin"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ADMIN PANEL ACCESS")
        elif normalized_path.startswith("/public"):
            response_body = "Public API response\n\nReceived Headers:\n"
            for h,v in self.headers.items():
                print(f"{h}: {v}")
                response_body += f"{h}: {v}\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(response_body.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    print("Starting monolith public backend on port 8080")
    HTTPServer(("0.0.0.0",8080), MonolithHandler).serve_forever()
