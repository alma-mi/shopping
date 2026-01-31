"""
Create User Dialog for Shopping App
Handles user registration interface
"""
import wx
from client import ShoppingClient
from constants import IP, PORT


class CreateUserDialog(wx.Dialog):
    """Dialog for creating a new user account"""

    def __init__(self, parent):
        super(
            CreateUserDialog,
            self).__init__(
            parent,
            title="Create New User",
            size=(
                800,
                800))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(15)

        # Build UI
        self._create_username_section(main_sizer)
        self._create_password_section(main_sizer)
        self._create_confirm_password_section(main_sizer)
        self._create_buttons_section(main_sizer)

        self.SetSizer(main_sizer)

    def _create_username_section(self, main_sizer):
        """Create username input section"""
        username_label = wx.StaticText(self, label="Username:")
        username_font = wx.Font(
            11,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD)
        username_label.SetFont(username_font)
        main_sizer.Add(username_label, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(5)

        self.username_entry = wx.TextCtrl(self, size=(400, 30))
        main_sizer.Add(self.username_entry, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(15)

    def _create_password_section(self, main_sizer):
        """Create password input section"""
        password_label = wx.StaticText(self, label="Password:")
        password_font = wx.Font(
            11,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD)
        password_label.SetFont(password_font)
        main_sizer.Add(password_label, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(5)

        self.password_entry = wx.TextCtrl(
            self, size=(400, 30), style=wx.TE_PASSWORD)
        main_sizer.Add(self.password_entry, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(15)

    def _create_confirm_password_section(self, main_sizer):
        """Create confirm password input section"""
        confirm_label = wx.StaticText(self, label="Confirm Password:")
        confirm_font = wx.Font(
            11,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD)
        confirm_label.SetFont(confirm_font)
        main_sizer.Add(confirm_label, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(5)

        self.confirm_entry = wx.TextCtrl(
            self, size=(400, 30), style=wx.TE_PASSWORD)
        main_sizer.Add(self.confirm_entry, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(20)

    def _create_buttons_section(self, main_sizer):
        """Create action buttons section"""
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddStretchSpacer(1)

        create_btn = wx.Button(self, label="Create", size=(120, 35))
        create_btn.SetBackgroundColour(wx.Colour(76, 175, 80))
        create_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        button_sizer.Add(create_btn, 0, wx.ALL, 10)

        cancel_btn = wx.Button(self, label="Cancel", size=(120, 35))
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        button_sizer.Add(cancel_btn, 0, wx.ALL, 10)

        button_sizer.AddStretchSpacer(1)
        main_sizer.Add(button_sizer, 0, wx.EXPAND)

    def _validate_inputs(self, username, password, confirm_password):
        """Validate user inputs. Returns (is_valid, error_message)"""
        if not username or not password:
            return False, "Please enter username and password"
        
        if password != confirm_password:
            return False, "Passwords do not match"
        
        return True, ""

    def _create_user_on_server(self, username, password):
        """Create user on server. Returns (success, error_message)"""
        try:
            client = ShoppingClient(IP, PORT)
            success = client.create_user(username, password)
            client.close()
            
            if success:
                return True, f"User '{username}' created successfully!"
            else:
                return False, "Failed to create user. Username may already exist."
        except Exception as e:
            return False, f"Error creating user:\n{str(e)}"

    def on_create(self, event):
        """Handle create user button click"""
        new_username = self.username_entry.GetValue().strip()
        new_password = self.password_entry.GetValue().strip()
        confirm_password = self.confirm_entry.GetValue().strip()

        # Validate inputs
        is_valid, error_msg = self._validate_inputs(
            new_username, new_password, confirm_password)
        
        if not is_valid:
            wx.MessageBox(error_msg, "Error", wx.OK | wx.ICON_ERROR)
            return

        # Create user on server
        success, message = self._create_user_on_server(
            new_username, new_password)
        
        if success:
            wx.MessageBox(message, "Success", wx.OK | wx.ICON_INFORMATION)
            self.EndModal(wx.ID_OK)
        else:
            wx.MessageBox(message, "Error", wx.OK | wx.ICON_ERROR)

