"""
Base GUI utilities and common components
Shared functionality across different GUI modules
"""
import wx
import os
from PIL import Image


class GUIConstants:
    """Common GUI constants and styling"""
    # Colors
    PRIMARY_COLOR = wx.Colour(33, 150, 243)
    SUCCESS_COLOR = wx.Colour(76, 175, 80)
    ERROR_COLOR = wx.Colour(244, 67, 54)
    WARNING_COLOR = wx.Colour(255, 152, 0)
    PURPLE_COLOR = wx.Colour(156, 39, 176)
    GRAY_COLOR = wx.Colour(128, 128, 128)
    LIGHT_GRAY = wx.Colour(200, 200, 200)
    WHITE = wx.Colour(255, 255, 255)

    # New gradient and theme colors
    BG_DARK = wx.Colour(15, 23, 42)  # Dark navy background
    BG_LIGHT = wx.Colour(241, 245, 250)  # Light background
    ACCENT_COLOR = wx.Colour(59, 130, 246)  # Bright blue accent
    TEXT_DARK = wx.Colour(30, 41, 59)  # Dark text
    TEXT_LIGHT = wx.Colour(100, 116, 139)  # Light gray text

    # Font sizes
    TITLE_SIZE = 24
    HEADING_SIZE = 12
    NORMAL_SIZE = 11
    SMALL_SIZE = 9

    # Dimensions
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 40
    PREVIEW_SIZE = (500, 350)


class GUIUtils:
    """Utility methods for creating and styling GUI components"""

    @staticmethod
    def create_styled_button(parent, label, color,
                             text_color=GUIConstants.WHITE):
        """Create a button with custom styling"""
        btn = wx.Button(parent, label=label)
        btn.SetBackgroundColour(color)
        btn.SetForegroundColour(text_color)
        return btn

    @staticmethod
    def create_styled_font(size=GUIConstants.NORMAL_SIZE,
                           weight=wx.FONTWEIGHT_NORMAL,
                           style=wx.FONTSTYLE_NORMAL):
        """Create a styled font"""
        return wx.Font(size, wx.FONTFAMILY_DEFAULT, style, weight)

    @staticmethod
    def load_image_preview(image_path, max_size=GUIConstants.PREVIEW_SIZE):
        """Load and prepare image for preview"""
        try:
            img = Image.open(image_path).convert('RGB')
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Keep full image visible by centering it inside a fixed preview box.
            preview_box = Image.new('RGB', max_size, (245, 245, 245))
            x = (max_size[0] - img.width) // 2
            y = (max_size[1] - img.height) // 2
            preview_box.paste(img, (x, y))

            width, height = preview_box.size
            wx_image = wx.Image(width, height)
            wx_image.SetData(preview_box.tobytes())

            return wx.Bitmap(wx_image)
        except Exception as e:
            raise Exception(f"Could not load image: {str(e)}")
