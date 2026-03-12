from http.server import HTTPServer, BaseHTTPRequestHandler

class AdminHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("\n[ADMIN SERVICE] Received Request")
        print(f"Command: {self.command}, Path: {self.path}")

        if self.path == "/admin/secrets":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"CONFIDENTIAL DATA: The cake is a lie.")
        elif self.path.startswith("/admin"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ADMIN PANEL ACCESS")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    print("Starting admin service on port 8081")
    HTTPServer(("0.0.0.0",8081), AdminHandler).serve_forever()
