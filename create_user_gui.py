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
                450,
                320))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddSpacer(15)

        # Username section
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

        # Password section
        password_label = wx.StaticText(self, label="Password:")
        password_label.SetFont(username_font)
        main_sizer.Add(password_label, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(5)

        self.password_entry = wx.TextCtrl(
            self, size=(400, 30), style=wx.TE_PASSWORD)
        main_sizer.Add(self.password_entry, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(15)

        # Confirm password section
        confirm_label = wx.StaticText(self, label="Confirm Password:")
        confirm_label.SetFont(username_font)
        main_sizer.Add(confirm_label, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(5)

        self.confirm_entry = wx.TextCtrl(
            self, size=(400, 30), style=wx.TE_PASSWORD)
        main_sizer.Add(self.confirm_entry, 0, wx.LEFT | wx.RIGHT, 20)
        main_sizer.AddSpacer(20)

        # Buttons
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

        self.SetSizer(main_sizer)

    def on_create(self, event):
        """Handle create user button click"""
        new_username = self.username_entry.GetValue().strip()
        new_password = self.password_entry.GetValue().strip()
        confirm_password = self.confirm_entry.GetValue().strip()

        if not new_username or not new_password:
            wx.MessageBox(
                "Please enter username and password",
                "Error",
                wx.OK | wx.ICON_ERROR)
            return

        if new_password != confirm_password:
            wx.MessageBox(
                "Passwords do not match",
                "Error",
                wx.OK | wx.ICON_ERROR)
            return

        try:
            client = ShoppingClient(IP, PORT)
            success = client.create_user(new_username, new_password)
            client.close()

            if success:
                wx.MessageBox(
                    f"User '{new_username}' created successfully!",
                    "Success",
                    wx.OK | wx.ICON_INFORMATION)
                self.EndModal(wx.ID_OK)
            else:
                wx.MessageBox(
                    "Failed to create user. Username may already exist.",
                    "Error",
                    wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(
                f"Error creating user:\n{str(e)}",
                "Connection Error",
                wx.OK | wx.ICON_ERROR)
