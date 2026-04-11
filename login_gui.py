"""
Login GUI module
Handles user authentication and new user creation
"""
import wx
from base_gui import GUIConstants, GUIUtils
from create_user_gui import CreateUserDialog


class LoginGUI:
    """Handles login screen display and authentication"""

    def __init__(self, main_frame):
        self.main_frame = main_frame
        self.username_entry = None
        self.password_entry = None

    def show_login_screen(self):
        """Display basic, normal website-style login interface"""
        # Clear panel
        self.main_frame.main_sizer.Clear(True)

        # Set white background like a normal website
        self.main_frame.main_panel.SetBackgroundColour(
            wx.Colour(255, 255, 255))

        # Create vertical sizer
        login_sizer = wx.BoxSizer(wx.VERTICAL)
        login_sizer.AddStretchSpacer(1)

        # Title - simple black text
        title = wx.StaticText(self.main_frame.main_panel, label="Shopping App")
        title_font = GUIUtils.create_styled_font(24, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(0, 0, 0))
        login_sizer.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        # Username
        self.username_entry = wx.TextCtrl(
            self.main_frame.main_panel, size=(300, 35),
            style=wx.TE_PROCESS_ENTER)
        self.username_entry.SetValue("")
        self.username_entry.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.username_entry.SetForegroundColour(wx.Colour(0, 0, 0))
        entry_font = GUIUtils.create_styled_font(16, wx.FONTWEIGHT_NORMAL)
        self.username_entry.SetFont(entry_font)
        self.username_entry.SetWindowStyle(wx.TE_PROCESS_ENTER)
        login_sizer.Add(self.username_entry, 0, wx.ALIGN_CENTER | wx.ALL, 8)

        # Password
        self.password_entry = wx.TextCtrl(
            self.main_frame.main_panel, size=(300, 35),
            style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.password_entry.SetValue("")
        self.password_entry.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.password_entry.SetForegroundColour(wx.Colour(0, 0, 0))
        self.password_entry.SetFont(entry_font)
        login_sizer.Add(self.password_entry, 0, wx.ALIGN_CENTER | wx.ALL, 8)

        # Login button - standard blue
        login_btn = wx.Button(
            self.main_frame.main_panel,
            label="Login")
        login_btn.SetSize((300, 35))
        login_btn.SetMinSize((300, 35))
        login_btn.SetBackgroundColour(wx.Colour(0, 102, 204))
        login_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        button_font = GUIUtils.create_styled_font(16, wx.FONTWEIGHT_BOLD)
        login_btn.SetFont(button_font)
        login_btn.Bind(wx.EVT_BUTTON, self.main_frame.on_login)
        login_sizer.Add(login_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        # New user button - simple gray
        create_user_btn = wx.Button(
            self.main_frame.main_panel,
            label="Create Account")
        create_user_btn.SetSize((300, 35))
        create_user_btn.SetMinSize((300, 35))
        create_user_btn.SetBackgroundColour(wx.Colour(128, 128, 128))
        create_user_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        create_user_btn.SetFont(button_font)
        create_user_btn.Bind(wx.EVT_BUTTON, self.main_frame.on_create_user)
        login_sizer.Add(create_user_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        login_sizer.AddStretchSpacer(1)

        self.main_frame.main_sizer.Add(
            login_sizer, 1, wx.EXPAND | wx.ALL, 0)
        self.main_frame.main_panel.Layout()

        # Bind Enter key
        self.username_entry.Bind(wx.EVT_TEXT_ENTER, self.main_frame.on_login)
        self.password_entry.Bind(wx.EVT_TEXT_ENTER, self.main_frame.on_login)

    def get_credentials(self):
        """Get username and password from input fields"""
        username = self.username_entry.GetValue().strip()
        password = self.password_entry.GetValue().strip()
        return username, password
