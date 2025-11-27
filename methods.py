"""
Server-side methods for shopping app
Handles authentication, product search, and session management
"""
import uuid
import time
from constants import SESSIONS, MAX_IMAGE_SIZE
from google_search import google_search_for_product
from chatgpt_search import analyze_image_for_products
import json
import protocol
from db import verify_user, get_user, add_user

MAX_PARAMS = 2
MIN_PARAMS = 0
PARAMS_ONE = 1
IMAGE_CHUNK_SIZE = 4096
BYTE = 1024


class Methods(object):

    @staticmethod
    def LOGIN(my_socket, params, address):
        """
        Authenticate user with username and password
        params: [username, password]
        Returns: JSON with session_id or error
        """
        if not params or len(params) < MAX_PARAMS:
            msg = "Username and password required"
            return json.dumps({"status": "error", "message": msg})

        username = params[MIN_PARAMS]
        password = params[PARAMS_ONE]

        # Check credentials using DB helpers
        user_record = get_user(username)
        if user_record is None:
            return json.dumps(
                {"status": "error", "message": "User does not exist"})

        verified = verify_user(username, password)
        if not verified:
            return json.dumps(
                {"status": "error", "message": "Incorrect password"})

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

    @staticmethod
    def CREATE_USER(my_socket, params, address):
        """
        Create a new user account
        params: [username, password]
        Returns: JSON with success or error
        """
        if not params or len(params) < MAX_PARAMS:
            return json.dumps({"status": "error",
                               "message": "Username and password required"})

        username = params[MIN_PARAMS]
        password = params[PARAMS_ONE]

        # Validate inputs
        if not username or not password:
            msg = "Username and password cannot be empty"
            return json.dumps(
                {"status": "error", "message": msg})

        # Check if user already exists
        existing_user = get_user(username)
        if existing_user is not None:
            return json.dumps(
                {"status": "error", "message": "Username already exists"})

        # Add user to database
        success = add_user(username, password)

        if success:
            return json.dumps({
                "status": "success",
                "message": f"User '{username}' created successfully"
            })
        else:
            return json.dumps({
                "status": "error",
                "message": "Failed to create user"
            })

    @staticmethod
    def SEARCH_PRODUCT(my_socket, params, address):
        """
        Search for products using Google Shopping API
        params: [session_id, product_query]
        Returns: JSON with product list or error
        """
        if not params or len(params) < MAX_PARAMS:
            msg = "Session ID and product query required"
            return json.dumps(
                {"status": "error", "message": msg})

        session_id = params[MIN_PARAMS]
        # Join remaining params as query
        product_query = ' '.join(params[PARAMS_ONE:])

        # Validate session
        if session_id not in SESSIONS:
            err_msg = "Invalid session. Please login again."
            return json.dumps(
                {"status": "error", "message": err_msg})

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
        if not params or len(params) < PARAMS_ONE:
            return json.dumps(
                {"status": "error", "message": "Session ID required"})

        session_id = params[MIN_PARAMS]

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
        """
        if not params or len(params) < PARAMS_ONE:
            return json.dumps(
                {"status": "error", "message": "Session ID required"})

        session_id = params[MIN_PARAMS]

        # Validate session
        if session_id not in SESSIONS:
            err_msg = "Invalid session. Please login again."
            return json.dumps(
                {"status": "error", "message": err_msg})

        try:
            # Receive image size
            size_data = protocol.Protocol.recv(my_socket)
            if not size_data:
                return json.dumps({"status": "error",
                                   "message": "Failed to receive image size"})

            image_size = int(size_data.decode())

            # Check image size limit
            if image_size > MAX_IMAGE_SIZE:
                size_mb = MAX_IMAGE_SIZE / (BYTE * BYTE)
                msg = f"Image too large. Max size is {size_mb}MB"
                return json.dumps({
                    "status": "error",
                    "message": msg
                })

            # Receive image data
            image_data = b""
            while len(image_data) < image_size:
                chunk = my_socket.recv(
                    min(IMAGE_CHUNK_SIZE, image_size - len(image_data)))
                if not chunk:
                    break
                image_data += chunk

            if len(image_data) != image_size:
                exp = image_size
                got = len(image_data)
                msg = f"Incomplete image data. Expected {exp}, got {got}"
                return json.dumps({
                    "status": "error",
                    "message": msg
                })

            search_terms, error = analyze_image_for_products(
                image_bytes=image_data)

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
                "message": (
                    f"Found {len(products)} products for "
                    f"'{search_terms}'"
                )
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
