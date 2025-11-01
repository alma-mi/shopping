"""
Shopping App Socket Client
Communicates with server using custom socket protocol
"""
import socket
import sys
import json
import protocol
from constants import IP, PORT


EXIT = 1


class ShoppingClient(object):
    def __init__(self, ip, port):
        """Initialize client socket and connect to server"""
        try:
            self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.my_socket.connect((ip, port))
            self.session_id = None
            self.username = None
            print(f"Connected to server at {ip}:{port}")
        except socket.error as msg:
            print(f'Connection failure: {msg}\nTerminating program')
            sys.exit(EXIT)

    def send_command(self, command):
        """
        Send command to server and receive response
        Returns: parsed JSON response or None
        """
        try:
            # Send command
            protocol.Protocol.send(self.my_socket, command)
            
            # Receive response
            response = protocol.Protocol.recv(self.my_socket)
            
            if not response:
                return None
            
            # Parse JSON response
            return json.loads(response.decode())
            
        except socket.error as msg:
            print(f"Socket error: {msg}")
            return None
        except json.JSONDecodeError as msg:
            print(f"JSON decode error: {msg}")
            return None
        except Exception as msg:
            print(f"Error: {msg}")
            return None

    def login(self, username, password):
        """
        Login to server
        Returns: True if successful, False otherwise
        """
        command = f"LOGIN {username} {password}"
        response = self.send_command(command)
        
        if response and response.get("status") == "success":
            self.session_id = response.get("session_id")
            self.username = response.get("username")
            return True
        return False

    def search_product(self, query):
        """
        Search for products
        Returns: list of products or None
        """
        if not self.session_id:
            print("Not logged in")
            return None
        
        command = f"SEARCH_PRODUCT {self.session_id} {query}"
        response = self.send_command(command)
        
        if response and response.get("status") == "success":
            return response.get("products", [])
        return None

    def logout(self):
        """Logout from server"""
        if not self.session_id:
            return True
        
        command = f"LOGOUT {self.session_id}"
        response = self.send_command(command)
        
        if response and response.get("status") == "success":
            self.session_id = None
            self.username = None
            return True
        return False

    def close(self):
        """Close connection to server"""
        try:
            self.send_command("EXIT")
            self.my_socket.close()
        except:
            pass


def main():
    """Test client with command line interface"""
    client = ShoppingClient(IP, PORT)
    
    print("=" * 50)
    print("Shopping App Client")
    print("=" * 50)
    
    # Login
    username = input("Username: ")
    password = input("Password: ")
    
    if client.login(username, password):
        print(f"\n✓ Logged in as {client.username}")
        
        while True:
            print("\nCommands: search <query>, logout, exit")
            cmd = input("> ").strip()
            
            if cmd.lower() == "exit":
                break
            elif cmd.lower() == "logout":
                if client.logout():
                    print("✓ Logged out")
                break
            elif cmd.lower().startswith("search "):
                query = cmd[7:]
                products = client.search_product(query)
                
                if products:
                    print(f"\nFound {len(products)} products:")
                    for i, product in enumerate(products[:5], 1):  # Show first 5
                        print(f"\n{i}. {product['name']}")
                        print(f"   Price: {product['price']}")
                        print(f"   Source: {product['source']}")
                        print(f"   Rating: {product.get('rating', 'N/A')}")
                else:
                    print("No products found")
            else:
                print("Unknown command")
    else:
        print("\n✗ Login failed")
    
    client.close()
    print("\nDisconnected")


if __name__ == '__main__':
    main()
