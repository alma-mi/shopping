"""
Camera GUI module
Handles camera capture and photo operations
"""
import wx
import cv2
import tempfile
import threading
import time
from constants import (CAMERA_BUTTON_WIDTH, CAMERA_BUTTON_HEIGHT,
                       CAMERA_BUTTON_OFFSET_Y, CAMERA_FONT_SIZE,
                       CAMERA_FONT_THICKNESS,
                       CAMERA_INSTRUCTIONS_FONT_SIZE,
                       CAMERA_TEXT_POSITION_X, CAMERA_TEXT_POSITION_Y,
                       CAMERA_CAPTURE_DEVICE, VIDEO_FRAME_DELAY_MS,
                       ESC_KEY_CODE, FLIP_HORIZONTAL)


class CameraGUI:
    """Handles camera functionality"""

    def __init__(self, main_frame):
        self.main_frame = main_frame

    def show_camera_instructions(self):
        """Show camera usage instructions"""
        wx.MessageBox(
            "Camera window will open.\n"
            "Click the green button to capture\n"
            "Press ESC to exit without capturing",
            "Camera Instructions",
            wx.OK | wx.ICON_INFORMATION)

    def capture_photo_async(self):
        """Capture photo in background thread"""
        def capture_thread():
            image_path = self.capture_photo()
            if image_path:
                wx.CallAfter(self.main_frame._set_captured_image, image_path)

        threading.Thread(target=capture_thread, daemon=True).start()

    def capture_photo(self):
        """Capture photo from camera using OpenCV"""
        try:
            cap = cv2.VideoCapture(CAMERA_CAPTURE_DEVICE)

            if not cap.isOpened():
                wx.MessageBox(
                    "Could not access camera",
                    "Camera Error",
                    wx.OK | wx.ICON_ERROR)
                return None

            captured_image = None
            button_info = {}
            capture_ready = [False]

            def mouse_click(event, x, y, flags, param):
                """Handle mouse clicks on camera window"""
                if event == cv2.EVENT_LBUTTONDOWN:
                    button = button_info
                    if (button.get('x1', 0) <= x <= button.get('x2', 0) and
                            button.get('y1', 0) <= y <= button.get('y2', 0)):
                        capture_ready[0] = True

            cv2.namedWindow("Camera - Click Button to Capture")
            cv2.setMouseCallback(
                "Camera - Click Button to Capture", mouse_click)

            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Flip frame for mirror effect
                frame = cv2.flip(frame, FLIP_HORIZONTAL)
                clean_frame = frame.copy()
                height, width = frame.shape[:2]

                # Draw capture button
                button_width = CAMERA_BUTTON_WIDTH
                button_height = CAMERA_BUTTON_HEIGHT
                button_x = (width - button_width) // 2
                button_y = height - CAMERA_BUTTON_OFFSET_Y

                # Store button coordinates for click detection
                button_info['x1'] = button_x
                button_info['y1'] = button_y
                button_info['x2'] = button_x + button_width
                button_info['y2'] = button_y + button_height

                # Draw button background
                cv2.rectangle(
                    frame,
                    (button_x, button_y),
                    (button_x + button_width, button_y + button_height),
                    (0, 255, 0),
                    -1)

                # Draw button text
                cv2.putText(
                    frame,
                    "CLICK TO CAPTURE",
                    (button_x + 5, button_y + 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    CAMERA_FONT_SIZE,
                    (0, 0, 0),
                    CAMERA_FONT_THICKNESS)

                # Display instructions
                cv2.putText(
                    frame,
                    "Click button above to capture | Press ESC to exit",
                    (CAMERA_TEXT_POSITION_X, CAMERA_TEXT_POSITION_Y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    CAMERA_INSTRUCTIONS_FONT_SIZE,
                    (0, 255, 0),
                    CAMERA_FONT_THICKNESS)

                cv2.imshow("Camera - Click Button to Capture", frame)

                if capture_ready[0]:
                    captured_image = clean_frame
                    break

                key = cv2.waitKey(VIDEO_FRAME_DELAY_MS) & 0xFF
                if key == ESC_KEY_CODE:  # ESC key
                    break

            cap.release()
            cv2.destroyAllWindows()
            # Small delay to ensure camera is fully released
            time.sleep(0.5)

            if captured_image is not None:
                # Save captured image
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix='.jpg')
                cv2.imwrite(temp_file.name, captured_image)
                temp_file.close()
                return temp_file.name

            return None

        except Exception as e:
            wx.MessageBox(
                f"Error capturing photo: {str(e)}",
                "Camera Error",
                wx.OK | wx.ICON_ERROR)
            return None
