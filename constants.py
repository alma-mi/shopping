"""
Constants for shopping app client/server
"""

# Server configuration
IP = "127.0.0.1"
PORT = 8766

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

# GUI Window Dimensions
GUI_WINDOW_WIDTH = 800
GUI_WINDOW_HEIGHT = 800

# GUI Layout Spacing
SPACING_LARGE = 20
SPACING_MEDIUM = 10
SPACING_SMALL = 5

# Camera Constants
CAMERA_BUTTON_WIDTH = 150
CAMERA_BUTTON_HEIGHT = 50
CAMERA_BUTTON_OFFSET_Y = 80
CAMERA_FONT_SIZE = 0.5
CAMERA_FONT_THICKNESS = 2
CAMERA_INSTRUCTIONS_FONT_SIZE = 0.6
CAMERA_TEXT_POSITION_X = 10
CAMERA_TEXT_POSITION_Y = 30

# Image Processing
IMAGE_PREVIEW_WIDTH = 200
IMAGE_PREVIEW_HEIGHT = 200
CAMERA_CAPTURE_DEVICE = 0
VIDEO_FRAME_DELAY_MS = 1
ESC_KEY_CODE = 27
FLIP_HORIZONTAL = 1

# Search Results
MAX_DISPLAY_RESULTS = 10
STAR_RATING_CHAR = "*"

# Protocol/Socket Settings
PROTOCOL_LENGTH_PREFIX = 4
SOCKET_CHUNK_SIZE = 4096
SOCKET_TIMEOUT = 5
MAX_LISTEN_BACKLOG = 5
IMAGE_CHUNK_SIZE = 4096
BYTE_CONVERSION = 1024

# Array/List Indices
FIRST_ELEMENT = 0
SECOND_ELEMENT = 1
MIN_INDEX = 0
MAX_INDEX = 1

# Numeric Constants
ZERO = 0
ONE = 1
TWO = 2
THREE = 3

# API Response Indices
PARAMS_FIRST = 0
PARAMS_SECOND = 1

# Default/Placeholder Values
DEFAULT_IMAGE_URL = "#"
DEFAULT_NOT_AVAILABLE = "N/A"
DEFAULT_NO_IMAGE = ""

# OpenAI Settings
GPT4_MAX_TOKENS = 100
GPT4_TEMPERATURE = 0.3
