"""
Constants for shopping app client/server
"""

# Server configuration
IP = "127.0.0.1"
PORT = 8765

# User storage (in-memory database)
# Format: {username: password}
USERS = {
    "admin": "admin123",
    "user": "password",
    "demo": "demo"
}

# Session storage (in-memory)
# Format: {session_id: {"username": str, "login_time": timestamp}}
SESSIONS = {}

# EOF marker for file transfers
EOF = b'EOF'

# Image transfer settings
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB max image size
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
