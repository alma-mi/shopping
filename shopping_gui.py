"""
Shopping App GUI using wxPython
Provides graphical interface for login, product search, and results display
Modular architecture with separated concerns for cleaner code organization
"""
import wx
import threading
from client import ShoppingClient
from constants import IP, PORT, GUI_WINDOW_WIDTH, GUI_WINDOW_HEIGHT
from create_user_gui import CreateUserDialog

# Import modular GUI components
from login_gui import LoginGUI
from search_gui import SearchGUI
from results_gui import ResultsGUI
from camera_gui import CameraGUI
from base_gui import GUIConstants


class ShoppingGUI(wx.Frame):
    """Main Shopping Application Frame - Orchestrates all GUI modules"""

    def __init__(self):
        super(
            ShoppingGUI,
            self).__init__(
            None,
            title='Shopping App',
            size=(
                GUI_WINDOW_WIDTH,
                GUI_WINDOW_HEIGHT))

        self.client = None
        self.session_id = None
        self.username = None

        # Create main panel
        self.main_panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.main_sizer)

        # Initialize GUI modules
        self.login_gui = LoginGUI(self)
        self.search_gui = SearchGUI(self)
        self.results_gui = ResultsGUI(self)
        self.camera_gui = CameraGUI(self)

        # Show login screen initially
        self.login_gui.show_login_screen()

        self.Centre()
        self.Show()

    # --- Login and Authentication ---

    def show_login_screen(self):
        """Display login interface"""
        self.login_gui.show_login_screen()

    def on_login(self, event):
        """Handle login button click"""
        username, password = self.login_gui.get_credentials()

        if not username or not password:
            wx.MessageBox(
                "Please enter username and password",
                "Error",
                wx.OK | wx.ICON_ERROR)
            return

        # Connect to server and login
        try:
            self.client = ShoppingClient(IP, PORT)

            if self.client.login(username, password):
                self.username = self.client.username
                self.session_id = self.client.session_id
                wx.MessageBox(
                    f"Welcome, {self.username}!",
                    "Success",
                    wx.OK | wx.ICON_INFORMATION)
                self.show_shopping_screen()
            else:
                wx.MessageBox(
                    "Invalid username or password",
                    "Error",
                    wx.OK | wx.ICON_ERROR)
                self.client = None
        except Exception as e:
            wx.MessageBox(
                f"Could not connect to server:\n{str(e)}",
                "Connection Error",
                wx.OK | wx.ICON_ERROR)

    def on_create_user(self, event):
        """Handle create new user button click"""
        dialog = CreateUserDialog(self)
        dialog.ShowModal()
        dialog.Destroy()

    # --- Main Shopping Screen ---

    def show_shopping_screen(self):
        """Display main shopping interface"""
        # Clear panel
        self.main_sizer.Clear(True)

        # Set white background like login page
        self.main_panel.SetBackgroundColour(wx.Colour(255, 255, 255))

        # Build UI components using modular GUIs
        self._create_top_bar()
        self.search_gui.create_search_panel()
        self.results_gui.create_results_panel()

        # Initial message
        self.results_gui.show_initial_message()

        self.main_panel.Layout()

    # --- Top Navigation Bar ---

    def _create_top_bar(self):
        """Create top navigation bar with welcome and logout"""
        top_panel = wx.Panel(self.main_panel)
        top_panel.SetBackgroundColour(wx.Colour(0, 102, 204))
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Welcome message
        welcome_label = wx.StaticText(
            top_panel, label=f"Welcome, {self.username}!")
        welcome_font = wx.Font(
            12,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD)
        welcome_label.SetFont(welcome_font)
        welcome_label.SetForegroundColour(wx.Colour(255, 255, 255))
        top_sizer.Add(
            welcome_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        top_sizer.AddStretchSpacer(1)

        # Logout button
        logout_btn = wx.Button(top_panel, label="Logout", size=(100, 30))
        logout_btn.SetBackgroundColour(wx.Colour(128, 128, 128))
        logout_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        logout_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        logout_btn.Bind(wx.EVT_BUTTON, self.on_logout)
        top_sizer.Add(logout_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)

        top_panel.SetSizer(top_sizer)
        self.main_sizer.Add(top_panel, 0, wx.EXPAND)

    # --- Image Search and Selection ---

    def on_select_image(self, event):
        """Handle image selection"""
        self.search_gui.select_image()

    # --- Image Search Operations ---

    def on_image_search(self, event):
        """Handle image-based product search"""
        image_path = self.search_gui.get_selected_image_path()

        if not image_path:
            wx.MessageBox(
                "Please select an image first",
                "Warning",
                wx.OK | wx.ICON_WARNING)
            return

        # Show loading message
        self.results_gui.show_loading_message(
            "Analyzing image and searching...")

        # Search in background thread
        def search_thread():
            products, search_terms = self.client.image_search(
                image_path)
            wx.CallAfter(self.results_gui.display_image_results,
                         products, search_terms)

        threading.Thread(target=search_thread, daemon=True).start()

    # --- Text Search (Legacy Support) ---

    def on_search(self, event):
        """Handle product search (keeping old text search for compatibility)"""
        query = self.search_entry.GetValue().strip()

        if not query:
            wx.MessageBox(
                "Please enter a product name",
                "Warning",
                wx.OK | wx.ICON_WARNING)
            return

        # Show loading message
        self.results_gui.show_loading_message("Searching...")

        # Search in background thread
        def search_thread():
            products = self.client.search_product(query)
            wx.CallAfter(self.results_gui.display_text_results,
                         products, query)

        threading.Thread(target=search_thread, daemon=True).start()

    # --- Camera Operations ---

    def on_take_photo(self, event):
        """Handle camera/photo capture"""
        self.camera_gui.show_camera_instructions()
        self.camera_gui.capture_photo_async()

    def _set_captured_image(self, image_path):
        """Set captured image and update UI"""
        self.search_gui.set_captured_image(image_path)

        wx.MessageBox(
            "Photo captured successfully!",
            "Success",
            wx.OK | wx.ICON_INFORMATION)

    # --- Session Management ---

    def on_logout(self, event):
        """Handle logout"""
        if self.client:
            self.client.logout()
            self.client.close()

        self.client = None
        self.session_id = None
        self.username = None

        wx.MessageBox(
            "You have been logged out",
            "Logged Out",
            wx.OK | wx.ICON_INFORMATION)
        self.show_login_screen()


def main():
    """Entry point for the application"""
    app = wx.App()
    ShoppingGUI()
    app.MainLoop()


if __name__ == "__main__":
    main()
