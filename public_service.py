from http.server import HTTPServer, BaseHTTPRequestHandler

class PublicHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("\n[PUBLIC SERVICE]")
        print(self.command, self.path)

        for h,v in self.headers.items():
            print(f"{h}: {v}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Public API response")

if __name__ == "__main__":
    print("Starting public service on port 8080")
    HTTPServer(("0.0.0.0",8080), PublicHandler).serve_forever()
