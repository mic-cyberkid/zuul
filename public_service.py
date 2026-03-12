from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os

class MonolithHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def do_GET(self):
        print(f"\n[BACKEND 8080] Received Request: {self.path}")
        for h,v in self.headers.items():
             print(f"  {h}: {v}")

        decoded_path = urllib.parse.unquote(self.path)

        if "/admin/secrets" in decoded_path:
            content = b"CONFIDENTIAL DATA: The cake is a lie."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif "/admin" in decoded_path:
            content = b"ADMIN PANEL ACCESS"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif "/public" in decoded_path:
            headers_str = ""
            for h,v in self.headers.items():
                headers_str += f"{h}: {v}\n"

            response_body = f"Public API response\n\nReceived Headers:\n{headers_str}"
            content = response_body.encode()

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            content = b"Not Found"
            self.send_response(404)
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)

if __name__ == "__main__":
    print("Starting robust monolith public backend on port 8080")
    HTTPServer(("0.0.0.0",8080), MonolithHandler).serve_forever()
