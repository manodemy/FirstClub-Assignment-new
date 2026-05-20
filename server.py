import sys
import os
import urllib.request
import urllib.parse
import http.server
import socketserver
import webbrowser
from compile_html import compile_html

PORT = 8000

class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Allow CORS so that even if opened via file://, the page can query this local server
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def do_GET(self):
        # Parse query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == '/proxy-sync':
            query_params = urllib.parse.parse_qs(parsed_url.query)
            sheet_url = query_params.get('url', [None])[0]
            
            if not sheet_url:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing 'url' parameter")
                return

            try:
                print(f"[Proxy] Syncing Google Sheet URL: {sheet_url}")
                
                # Re-encode the URL to handle spaces / special chars in tab names
                # urllib may receive a partially-decoded URL from the browser
                parsed = urllib.parse.urlparse(sheet_url)
                safe_query = urllib.parse.urlencode(
                    urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
                )
                safe_url = urllib.parse.urlunparse(parsed._replace(query=safe_query))
                print(f"[Proxy] Safe URL: {safe_url}")
                
                # Fetch CSV from Google Sheets
                req = urllib.request.Request(
                    safe_url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    csv_bytes = response.read()
                
                csv_text = csv_bytes.decode('utf-8')
                
                # Check for basic CSV format (has headers) to prevent saving HTML login pages
                if "Date" in csv_text and ("Revenue" in csv_text or "FSN" in csv_text):
                    # Write to raw_transaction_data.csv
                    csv_path = os.path.join(os.getcwd(), "raw_transaction_data.csv")
                    with open(csv_path, "wb") as f:
                        f.write(csv_bytes)
                    print(f"[Proxy] Successfully saved raw transaction data to: {csv_path}")
                    
                    # Recompile index.html using the helper script
                    print("[Proxy] Recompiling index.html with new data slice...")
                    try:
                        compile_html()
                        print("[Proxy] Recompilation successful.")
                    except Exception as compile_err:
                        print(f"[Proxy] Warning: Recompilation failed: {compile_err}")
                    
                    # Return CSV back to client
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(csv_bytes)
                else:
                    # If it's a web login page or not a CSV
                    snippet = csv_text[:200].replace('\n', ' ')
                    msg = (
                        f"Sheet is either private or the tab name is wrong.\n"
                        f"Fix: Share the Google Sheet as 'Anyone with the link can view'.\n"
                        f"Also make sure the Tab Name field matches exactly (e.g. 'Sheet1').\n"
                        f"Response preview: {snippet}"
                    )
                    print(f"[Proxy] Error: {msg}")
                    self.send_response(422)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(msg.encode('utf-8'))
                    
            except Exception as e:
                msg = f"Proxy fetch error: {type(e).__name__}: {e}"
                print(f"[Proxy] {msg}")
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(msg.encode('utf-8'))

        else:
            # Fallback to serving index.html as default if path is empty or /
            if parsed_url.path == '/' or parsed_url.path == '':
                self.path = '/index.html'
            super().do_GET()

def run_server():
    # Change working directory to the directory of this script to avoid path confusion
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir:
        os.chdir(script_dir)
    
    # Try running the server
    handler = DashboardRequestHandler
    
    # Allow port reuse to avoid 'Address already in use' errors on quick restarts
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"\n========================================================")
        print(f" FirstClub Assignment Category Intelligence Dashboard Local Server")
        print(f"========================================================")
        print(f" Server running at: http://localhost:{PORT}")
        print(f" Bypassing CORS restrictions dynamically!")
        print(f" Autosaving synced Google Sheets -> raw_transaction_data.csv")
        print(f" Autorebuilding index.html for offline usage")
        print(f"========================================================")
        print(f"Press Ctrl+C in this terminal to stop the server.\n")
        
        # Open in web browser automatically
        webbrowser.open(f"http://localhost:{PORT}/")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped. Goodbye!")

if __name__ == "__main__":
    run_server()
