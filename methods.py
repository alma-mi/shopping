"""
Server-side methods for shopping app
Handles authentication, product search, and session management
"""
import uuid
import time
from constants import USERS, SESSIONS
from google_search import google_search_for_product
import json


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
    def EXIT(my_socket, params, address):
        """Close client connection"""
        return json.dumps({"status": "success", "message": "EXIT"})
