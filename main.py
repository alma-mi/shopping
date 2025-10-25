import socketserver
from dotenv import load_dotenv
from http_server import MyHTTPRequestHandler

load_dotenv()

if __name__ == "__main__":
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", 8088), Handler) as httpd:
        print(f"Server running at http://localhost:{8088}")
        httpd.serve_forever()
