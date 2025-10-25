import os
import uuid
import http.server
import socketserver
import urllib.parse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
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
        elif self.path.startswith("/?product_search"):
            self.handle_product_search()
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
                <form method="get" action="/">
                    <label>Search for product: </label>
                    <input type="text" id="product_search" name="product_search">
                    <button type="submit">Find</button>
                </form>
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

    def handle_product_search(self):
        """Handle product search requests using Google Search via SerpAPI"""
        user = self.get_current_user()
        
        if not user:
            # Redirect to signin if not authenticated
            self.send_response(302)
            self.send_header('Location', '/signin')
            self.end_headers()
            return
        
        # Parse query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        product_name = query_params.get('product_search', [''])[0]
        
        products = []
        error_message = ""
        
        if product_name and SERPAPI_KEY:
            try:
                # Search for products using SerpAPI Google Shopping
                params = {
                    "engine": "google_shopping",
                    "q": product_name,
                    "api_key": SERPAPI_KEY,
                    "num": 10  # Limit to 10 results
                }
                
                search = GoogleSearch(params)
                results = search.get_dict()
                
                if "shopping_results" in results:
                    for idx, item in enumerate(results["shopping_results"][:10]):
                        product = {
                            "id": idx + 1,
                            "name": item.get("title", "Unknown Product"),
                            "price": item.get("price", "Price not available"),
                            "source": item.get("source", "Unknown"),
                            "link": item.get("link", "#"),
                            "product_link": item.get("product_link", "#"),
                            "thumbnail": item.get("thumbnail", ""),
                            "rating": item.get("rating", 0),
                            "reviews": item.get("reviews", 0)
                        }
                        products.append(product)
                else:
                    error_message = "No shopping results found."
                    
            except Exception as e:
                error_message = f"Search error: {str(e)}"
        elif not SERPAPI_KEY:
            error_message = "SerpAPI key not configured. Please add SERPAPI_KEY to your .env file."
        
        # Generate HTML response
        products_html = ""
        if products:
            products_html = "<ul>"
            for product in products:
                rating_stars = "⭐" * int(product['rating']) if product['rating'] else "No rating"
                thumbnail_html = f'<img src="{product["thumbnail"]}" alt="{product["name"]}" width="100">' if product["thumbnail"] else ""
                products_html += f"""
                <li>
                    <h3><a href="{product['product_link']}" target="_blank">{product['name']}</a></h3>
                    {thumbnail_html}
                    <p>Price: {product['price']}</p>
                    <p>Source: {product['source']}</p>
                    <p>Rating: {rating_stars} ({product['reviews']} reviews)</p>
                </li>
                """
            products_html += "</ul>"
        elif error_message:
            products_html = f"<p>Error: {error_message}</p>"
        elif not product_name:
            products_html = "<p>Please enter a product name to search.</p>"
        else:
            products_html = f"<p>No products found for '{product_name}'. Try a different search term.</p>"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Shopping App - Search Results</title>
        </head>
        <body>
            <h1>Hello, {user['name']}!</h1>
            <form method="post" action="/logout">
                <button type="submit">Logout</button>
            </form>
            
            <form method="get" action="/">
                <label for="product_name">Search Products: </label>
                <input type="text" id="product_name" name="product_name" value="{product_name}">
                <button type="submit">Search</button>
            </form>
            
            <h2>Search Results{f" for '{product_name}'" if product_name else ""}</h2>
            {products_html}
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

if __name__ == "__main__":
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", 8088), Handler) as httpd:
        print(f"Server running at http://localhost:{8088}")
        httpd.serve_forever()
