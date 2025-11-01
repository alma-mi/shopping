"""
Test script for Shopping App socket implementation
Tests basic functionality without GUI
"""
from client import ShoppingClient
from constants import IP, PORT
import time


def test_client():
    print("=" * 60)
    print("Shopping App Test Suite")
    print("=" * 60)
    print("\nMake sure the server is running first!")
    print("Run: python server.py\n")
    
    input("Press Enter to start tests...")
    
    try:
        # Test 1: Connection
        print("\n[TEST 1] Connecting to server...")
        client = ShoppingClient(IP, PORT)
        print("✓ Connected successfully")
        
        # Test 2: Login with valid credentials
        print("\n[TEST 2] Testing login with valid credentials...")
        if client.login("admin", "admin123"):
            print(f"✓ Login successful - Session: {client.session_id}")
            print(f"✓ Username: {client.username}")
        else:
            print("✗ Login failed")
            return
        
        # Test 3: Invalid login
        print("\n[TEST 3] Testing login with invalid credentials...")
        client2 = ShoppingClient(IP, PORT)
        if not client2.login("invalid", "wrong"):
            print("✓ Correctly rejected invalid credentials")
        else:
            print("✗ Should have rejected invalid credentials")
        client2.close()
        
        # Test 4: Product search
        print("\n[TEST 4] Testing product search...")
        products = client.search_product("laptop")
        if products:
            print(f"✓ Search successful - Found {len(products)} products")
            if len(products) > 0:
                print(f"  First product: {products[0]['name']}")
                print(f"  Price: {products[0]['price']}")
        else:
            print("✗ Search returned no products (check SERPAPI_KEY in .env)")
        
        # Test 5: Search without session (should fail)
        print("\n[TEST 5] Testing search without valid session...")
        client3 = ShoppingClient(IP, PORT)
        client3.session_id = "invalid-session"
        result = client3.search_product("test")
        if result is None:
            print("✓ Correctly rejected invalid session")
        client3.close()
        
        # Test 6: Logout
        print("\n[TEST 6] Testing logout...")
        if client.logout():
            print("✓ Logout successful")
        else:
            print("✗ Logout failed")
        
        # Test 7: Search after logout (should fail)
        print("\n[TEST 7] Testing search after logout...")
        result = client.search_product("test")
        if result is None:
            print("✓ Correctly prevented search after logout")
        else:
            print("✗ Should not allow search after logout")
        
        # Cleanup
        client.close()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except ConnectionRefusedError:
        print("\n✗ ERROR: Could not connect to server")
        print("  Make sure the server is running:")
        print("  python server.py")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_client()
