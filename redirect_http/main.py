"""Simple script to redirect HTTP requests to HTTPS (or any other URL)."""

from http.server import HTTPServer, BaseHTTPRequestHandler


destination = "https://shove.cc"


# from https://stackoverflow.com/a/47084250/13216113

class RequestRedirect(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(301)
        self.send_header("Location", destination)
        self.end_headers()
        client_ip, client_port = self.client_address
        print(f"Redirected {client_ip}:{client_port}")


print(f"Redirecting HTTP traffic to {destination}!")
HTTPServer(("", 80), RequestRedirect).serve_forever()
