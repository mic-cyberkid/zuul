from http.server import HTTPServer, BaseHTTPRequestHandler

class AdminHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        print("\n[ADMIN SERVICE]")
        print(self.command, self.path)

        if self.path.startswith("/admin"):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ADMIN PANEL ACCESS")
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print("Starting admin service on port 8081")
    HTTPServer(("0.0.0.0",8081), AdminHandler).serve_forever()
