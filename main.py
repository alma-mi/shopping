import os
import uuid
import http.server
import socketserver
import urllib.parse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
sessions = {}

class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    def get_current_user(self):
        """Get current user from session cookie"""
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return None
            
        for cookie in cookie_header.split(';'):
            if cookie.strip().startswith('session_id='):
                session_id = cookie.split('=')[1].strip()
                return sessions.get(session_id)
        return None
    
    def set_cookie(self, name, value):
        """Set a cookie in response"""
        self.send_header('Set-Cookie', f'{name}={value}; Path=/; HttpOnly')
    
    def do_GET(self):
        if self.path == '/':
            self.handle_home()
        elif self.path == '/signin':
            self.handle_signin()
        elif self.path == '/logout':
            self.handle_logout()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/auth/google':
            self.handle_google_auth()
        elif self.path == '/logout':
            self.handle_logout()
        else:
            self.send_error(404)
    
    def handle_home(self):
        user = self.get_current_user()
        
        if user:
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Shopping App</title>
            </head>
            <body>
                <h1>Hello, {user['name']}!</h1>
                <form method="post" action="/logout">
                    <button type="submit">Logout</button>
                </form>
            </body>
            </html>
            """
        else:
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Shopping App</title>
            </head>
            <body>
                <h1>Shopping App</h1>
                <a href="/signin">
                    <button>Sign In</button>
                </a>
            </body>
            </html>
            """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_signin(self):
        if not GOOGLE_CLIENT_ID:
            self.send_error(501, "Google OAuth not configured")
            return
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sign In</title>
            <script src="https://accounts.google.com/gsi/client" async defer></script>
        </head>
        <body>
            <h1>Sign In with Google</h1>
            <div id="g_id_onload"
                 data-client_id="{GOOGLE_CLIENT_ID}"
                 data-login_uri="/auth/google"
                 data-auto_prompt="false">
            </div>
            <div class="g_id_signin"
                 data-type="standard"
                 data-size="large"
                 data-theme="outline"
                 data-text="sign_in_with"
                 data-shape="rectangular"
                 data-logo_alignment="left">
            </div>
        </body>
        </html>
        """
        
        self.send_response(200) # מחזיר תשובה OK
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_google_auth(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = urllib.parse.parse_qs(post_data)
        
        credential = form_data.get('credential', [None])[0]
        if not credential:
            self.send_error(400, "Missing credential")
            return
        
        try:
            # Verify the Google ID token
            idinfo = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                GOOGLE_CLIENT_ID
            )
            
            # Extract user information
            user_data = {
                "id": idinfo["sub"],
                "email": idinfo["email"],
                "name": idinfo["name"],
                "picture": idinfo.get("picture", "")
            }
            
            # Create session
            session_id = str(uuid.uuid4())
            sessions[session_id] = user_data
            
            # Redirect to home with session cookie
            self.send_response(302) # 
            self.send_header('Location', '/')
            self.set_cookie('session_id', session_id)
            self.end_headers()
            
        except Exception as e:
            self.send_error(400, f"Authentication error: {str(e)}")
    
    def handle_logout(self):
        # Clear session
        cookie_header = self.headers.get('Cookie')
        if cookie_header:
            for cookie in cookie_header.split(';'):
                if cookie.strip().startswith('session_id='):
                    session_id = cookie.split('=')[1].strip()
                    if session_id in sessions:
                        del sessions[session_id]
        
        # Redirect to home and clear cookie
        self.send_response(302)
        self.send_header('Location', '/')
        self.set_cookie('session_id', '')
        self.end_headers()

if __name__ == "__main__":
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", 8088), Handler) as httpd:
        print(f"Server running at http://localhost:{8088}")
        httpd.serve_forever()
