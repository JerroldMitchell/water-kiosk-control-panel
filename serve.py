#!/usr/bin/env python3
"""
Simple web server for viewing the dashboard mockup.
Serve the HTML file on localhost:8888
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Prevent caching for development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

    def log_message(self, format, *args):
        # Simple logging
        print(f"[{self.client_address[0]}] {format % args}")

def run_server(port=8888):
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)

    print(f"\n🚀 Dashboard mockup running at: http://localhost:{port}")
    print(f"📂 Serving files from: {os.getcwd()}")
    print(f"\n✅ Open http://localhost:{port}/dashboard.html in your browser")
    print(f"\n⎇ Press Ctrl+C to stop the server\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
        sys.exit(0)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    run_server(port)
