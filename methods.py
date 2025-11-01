"""
Server-side methods for shopping app
Handles authentication, product search, and session management
"""
import uuid
import time
from constants import USERS, SESSIONS, MAX_IMAGE_SIZE
from google_search import google_search_for_product
from chatgpt_search import analyze_image_for_products
import json
import protocol


class Methods(object):
    
    @staticmethod
    def LOGIN(my_socket, params, address):
        """
        Authenticate user with username and password
        params: [username, password]
        Returns: JSON with session_id or error
        """
        if not params or len(params) < 2:
            return json.dumps({"status": "error", "message": "Username and password required"})
        
        username = params[0]
        password = params[1]
        
        # Check credentials
        if username in USERS and USERS[username] == password:
            # Create session
            session_id = str(uuid.uuid4())
            SESSIONS[session_id] = {
                "username": username,
                "login_time": time.time(),
                "address": address
            }
            
            return json.dumps({
                "status": "success",
                "session_id": session_id,
                "username": username,
                "message": f"Welcome, {username}!"
            })
        else:
            return json.dumps({
                "status": "error",
                "message": "Invalid username or password"
            })
    
    @staticmethod
    def SEARCH_PRODUCT(my_socket, params, address):
        """
        Search for products using Google Shopping API
        params: [session_id, product_query]
        Returns: JSON with product list or error
        """
        if not params or len(params) < 2:
            return json.dumps({"status": "error", "message": "Session ID and product query required"})
        
        session_id = params[0]
        product_query = ' '.join(params[1:])  # Join remaining params as query
        
        # Validate session
        if session_id not in SESSIONS:
            return json.dumps({"status": "error", "message": "Invalid session. Please login again."})
        
        # Search for products
        products, error_message = google_search_for_product(product_query)
        
        if error_message:
            return json.dumps({
                "status": "error",
                "message": error_message
            })
        
        if not products:
            return json.dumps({
                "status": "success",
                "products": [],
                "message": f"No products found for '{product_query}'"
            })
        
        return json.dumps({
            "status": "success",
            "products": products,
            "query": product_query,
            "count": len(products)
        })
    
    @staticmethod
    def LOGOUT(my_socket, params, address):
        """
        Logout user and destroy session
        params: [session_id]
        Returns: JSON with success message
        """
        if not params or len(params) < 1:
            return json.dumps({"status": "error", "message": "Session ID required"})
        
        session_id = params[0]
        
        if session_id in SESSIONS:
            username = SESSIONS[session_id]["username"]
            del SESSIONS[session_id]
            return json.dumps({
                "status": "success",
                "message": f"Goodbye, {username}!"
            })
        else:
            return json.dumps({
                "status": "error",
                "message": "Invalid session"
            })
    
    @staticmethod
    def GET_SESSIONS(my_socket, params, address):
        """
        Get active sessions (for debugging)
        Returns: JSON with session count
        """
        return json.dumps({
            "status": "success",
            "active_sessions": len(SESSIONS),
            "sessions": list(SESSIONS.keys())
        })
    
    @staticmethod
    def IMAGE_SEARCH(my_socket, params, address):
        """
        Search for products using an uploaded image
        1. Receives image data from client
        2. Uses GPT-4 Vision to analyze image and extract search terms
        3. Searches for products using extracted terms
        
        params: [session_id]
        Returns: JSON with search terms and product list or error
        """
        if not params or len(params) < 1:
            return json.dumps({"status": "error", "message": "Session ID required"})
        
        session_id = params[0]
        
        # Validate session
        if session_id not in SESSIONS:
            return json.dumps({"status": "error", "message": "Invalid session. Please login again."})
        
        try:
            # Receive image size
            size_data = protocol.Protocol.recv(my_socket)
            if not size_data:
                return json.dumps({"status": "error", "message": "Failed to receive image size"})
            
            image_size = int(size_data.decode())
            
            # Check image size limit
            if image_size > MAX_IMAGE_SIZE:
                return json.dumps({
                    "status": "error", 
                    "message": f"Image too large. Max size is {MAX_IMAGE_SIZE / (1024*1024)}MB"
                })
            
            # Receive image data
            image_data = b""
            while len(image_data) < image_size:
                chunk = my_socket.recv(min(4096, image_size - len(image_data)))
                if not chunk:
                    break
                image_data += chunk
            
            if len(image_data) != image_size:
                return json.dumps({
                    "status": "error", 
                    "message": f"Incomplete image data. Expected {image_size}, got {len(image_data)}"
                })
            
            # Analyze image with GPT-4 Vision
            search_terms, error = analyze_image_for_products(image_bytes=image_data)
            
            if error:
                return json.dumps({
                    "status": "error",
                    "message": f"Image analysis failed: {error}"
                })
            
            if not search_terms:
                return json.dumps({
                    "status": "error",
                    "message": "Could not extract search terms from image"
                })
            
            # Search for products using extracted terms
            products, search_error = google_search_for_product(search_terms)
            
            if search_error:
                return json.dumps({
                    "status": "error",
                    "message": search_error,
                    "search_terms": search_terms
                })
            
            if not products:
                return json.dumps({
                    "status": "success",
                    "products": [],
                    "search_terms": search_terms,
                    "message": f"No products found for '{search_terms}'"
                })
            
            return json.dumps({
                "status": "success",
                "products": products,
                "search_terms": search_terms,
                "query": search_terms,
                "count": len(products),
                "message": f"Found {len(products)} products for '{search_terms}'"
            })
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Error processing image: {str(e)}"
            })
    
    @staticmethod
    def EXIT(my_socket, params, address):
        """Close client connection"""
        return json.dumps({"status": "success", "message": "EXIT"})
