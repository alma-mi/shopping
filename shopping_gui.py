"""
Shopping App GUI using wxPython
Provides graphical interface for login, product search, and results display
"""
import wx
import wx.lib.scrolledpanel as scrolled
from client import ShoppingClient
from constants import IP, PORT, SUPPORTED_IMAGE_FORMATS
import threading
import webbrowser
import os
from PIL import Image


class ShoppingGUI(wx.Frame):
    def __init__(self):
        super(ShoppingGUI, self).__init__(None, title='Shopping App', size=(800, 600))
        
        self.client = None
        self.session_id = None
        self.username = None
        
        # Create main panel
        self.main_panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(self.main_sizer)
        
        # Show login screen initially
        self.show_login_screen()
        
        self.Centre()
        self.Show()
    
    def show_login_screen(self):
        """Display login interface"""
        # Clear panel
        self.main_sizer.Clear(True)
        
        # Create vertical sizer for centered content
        login_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Add spacer to center vertically
        login_sizer.AddStretchSpacer(1)
        
        # Title
        title = wx.StaticText(self.main_panel, label="Shopping App")
        title_font = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        login_sizer.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        
        # Subtitle
        subtitle = wx.StaticText(self.main_panel, label="Login to search for products")
        subtitle_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        subtitle.SetFont(subtitle_font)
        login_sizer.Add(subtitle, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        # Username field
        username_label = wx.StaticText(self.main_panel, label="Username:")
        login_sizer.Add(username_label, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        
        self.username_entry = wx.TextCtrl(self.main_panel, size=(300, -1), style=wx.TE_PROCESS_ENTER)
        self.username_entry.SetValue("admin")
        login_sizer.Add(self.username_entry, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Password field
        password_label = wx.StaticText(self.main_panel, label="Password:")
        login_sizer.Add(password_label, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        
        self.password_entry = wx.TextCtrl(self.main_panel, size=(300, -1), style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.password_entry.SetValue("admin123")
        login_sizer.Add(self.password_entry, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Login button
        login_btn = wx.Button(self.main_panel, label="Login", size=(200, 40))
        login_btn.SetBackgroundColour(wx.Colour(76, 175, 80))
        login_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        login_sizer.Add(login_btn, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        
        # Info text
        info_text = wx.StaticText(self.main_panel, 
                                 label="Default credentials:\nUsername: admin | Password: admin123\nUsername: user | Password: password")
        info_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        info_text.SetFont(info_font)
        info_text.SetForegroundColour(wx.Colour(128, 128, 128))
        login_sizer.Add(info_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        login_sizer.AddStretchSpacer(1)
        
        self.main_sizer.Add(login_sizer, 1, wx.EXPAND | wx.ALL, 20)
        self.main_panel.Layout()
        
        # Bind Enter key
        self.username_entry.Bind(wx.EVT_TEXT_ENTER, self.on_login)
        self.password_entry.Bind(wx.EVT_TEXT_ENTER, self.on_login)
    
    def on_login(self, event):
        """Handle login button click"""
        username = self.username_entry.GetValue().strip()
        password = self.password_entry.GetValue().strip()
        
        if not username or not password:
            wx.MessageBox("Please enter username and password", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        # Connect to server and login
        try:
            self.client = ShoppingClient(IP, PORT)
            
            if self.client.login(username, password):
                self.username = self.client.username
                self.session_id = self.client.session_id
                wx.MessageBox(f"Welcome, {self.username}!", "Success", wx.OK | wx.ICON_INFORMATION)
                self.show_shopping_screen()
            else:
                wx.MessageBox("Invalid username or password", "Error", wx.OK | wx.ICON_ERROR)
                self.client = None
        except Exception as e:
            wx.MessageBox(f"Could not connect to server:\n{str(e)}", "Connection Error", wx.OK | wx.ICON_ERROR)
    
    def show_shopping_screen(self):
        """Display main shopping interface"""
        # Clear panel
        self.main_sizer.Clear(True)
        
        # Top bar
        top_panel = wx.Panel(self.main_panel)
        top_panel.SetBackgroundColour(wx.Colour(33, 150, 243))
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Welcome message
        welcome_label = wx.StaticText(top_panel, label=f"Welcome, {self.username}!")
        welcome_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        welcome_label.SetFont(welcome_font)
        welcome_label.SetForegroundColour(wx.Colour(255, 255, 255))
        top_sizer.Add(welcome_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        
        top_sizer.AddStretchSpacer(1)
        
        # Logout button
        logout_btn = wx.Button(top_panel, label="Logout")
        logout_btn.Bind(wx.EVT_BUTTON, self.on_logout)
        top_sizer.Add(logout_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 15)
        
        top_panel.SetSizer(top_sizer)
        self.main_sizer.Add(top_panel, 0, wx.EXPAND)
        
        # Search panel
        search_panel = wx.Panel(self.main_panel)
        search_sizer = wx.BoxSizer(wx.VERTICAL)
        
        search_label = wx.StaticText(search_panel, label="Search Products by Image:")
        search_label_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        search_label.SetFont(search_label_font)
        search_sizer.Add(search_label, 0, wx.ALL, 5)
        
        # Image upload section
        upload_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Upload button
        upload_btn = wx.Button(search_panel, label="📷 Select Image")
        upload_btn.SetBackgroundColour(wx.Colour(33, 150, 243))
        upload_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        upload_btn.Bind(wx.EVT_BUTTON, self.on_select_image)
        upload_sizer.Add(upload_btn, 0, wx.ALL, 5)
        
        # Selected image label
        self.image_path_label = wx.StaticText(search_panel, label="No image selected")
        self.image_path_label.SetForegroundColour(wx.Colour(128, 128, 128))
        upload_sizer.Add(self.image_path_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        # Search button (disabled until image is selected)
        self.search_btn = wx.Button(search_panel, label="Search by Image")
        self.search_btn.SetBackgroundColour(wx.Colour(76, 175, 80))
        self.search_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.search_btn.Bind(wx.EVT_BUTTON, self.on_image_search)
        self.search_btn.Enable(False)
        upload_sizer.Add(self.search_btn, 0, wx.ALL, 5)
        
        search_sizer.Add(upload_sizer, 0, wx.ALL, 5)
        
        # Image preview
        self.image_preview = wx.StaticBitmap(search_panel)
        search_sizer.Add(self.image_preview, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        
        # Store selected image path
        self.selected_image_path = None
        
        search_panel.SetSizer(search_sizer)
        self.main_sizer.Add(search_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        # Results panel (scrolled)
        results_label = wx.StaticText(self.main_panel, label="Results:")
        results_label_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        results_label.SetFont(results_label_font)
        self.main_sizer.Add(results_label, 0, wx.LEFT | wx.RIGHT, 20)
        
        self.results_panel = scrolled.ScrolledPanel(self.main_panel)
        self.results_panel.SetupScrolling()
        self.results_sizer = wx.BoxSizer(wx.VERTICAL)
        self.results_panel.SetSizer(self.results_sizer)
        self.main_sizer.Add(self.results_panel, 1, wx.EXPAND | wx.ALL, 10)
        
        # Initial message
        self.show_initial_message()
        
        self.main_panel.Layout()
    
    def show_initial_message(self):
        """Show initial message in results area"""
        self.results_sizer.Clear(True)
        
        msg = wx.StaticText(self.results_panel, label="Select an image to search for similar products...")
        msg_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        msg.SetFont(msg_font)
        msg.SetForegroundColour(wx.Colour(128, 128, 128))
        self.results_sizer.Add(msg, 0, wx.ALIGN_CENTER | wx.ALL, 50)
        
        self.results_panel.SetupScrolling()
        self.results_panel.Layout()
    
    def on_select_image(self, event):
        """Handle image selection"""
        # Create file dialog for image selection
        wildcard = "Image files (*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.webp)|*.jpg;*.jpeg;*.png;*.gif;*.bmp;*.webp"
        
        dialog = wx.FileDialog(
            self,
            message="Choose an image file",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        
        if dialog.ShowModal() == wx.ID_OK:
            self.selected_image_path = dialog.GetPath()
            filename = os.path.basename(self.selected_image_path)
            self.image_path_label.SetLabel(f"Selected: {filename}")
            self.search_btn.Enable(True)
            
            # Show image preview
            try:
                img = Image.open(self.selected_image_path)
                
                # Resize for preview (max 200x200)
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                # Convert to wx.Image
                width, height = img.size
                wx_image = wx.Image(width, height)
                wx_image.SetData(img.convert('RGB').tobytes())
                
                # Set to preview
                bitmap = wx.Bitmap(wx_image)
                self.image_preview.SetBitmap(bitmap)
                
            except Exception as e:
                wx.MessageBox(f"Could not load image preview: {str(e)}", "Warning", wx.OK | wx.ICON_WARNING)
        
        dialog.Destroy()
    
    def on_image_search(self, event):
        """Handle image-based product search"""
        if not self.selected_image_path:
            wx.MessageBox("Please select an image first", "Warning", wx.OK | wx.ICON_WARNING)
            return
        
        # Clear previous results
        self.results_sizer.Clear(True)
        
        # Show loading message
        loading = wx.StaticText(self.results_panel, label="Analyzing image and searching...")
        loading_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        loading.SetFont(loading_font)
        self.results_sizer.Add(loading, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        self.results_panel.Layout()
        
        # Search in background thread
        def search_thread():
            products, search_terms = self.client.image_search(self.selected_image_path)
            wx.CallAfter(self.display_image_results, products, search_terms)
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def display_image_results(self, products, search_terms):
        """Display search results from image search"""
        # Clear loading message
        self.results_sizer.Clear(True)
        
        # Check if there was an error
        if products is None:
            error_msg = wx.StaticText(self.results_panel, label=f"Error: {search_terms}")
            error_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            error_msg.SetFont(error_font)
            error_msg.SetForegroundColour(wx.Colour(255, 0, 0))
            self.results_sizer.Add(error_msg, 0, wx.ALIGN_CENTER | wx.ALL, 50)
            self.results_panel.SetupScrolling()
            self.results_panel.Layout()
            return
        
        # Show extracted search terms
        terms_label = wx.StaticText(self.results_panel, label=f"AI detected: {search_terms}")
        terms_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_BOLD)
        terms_label.SetFont(terms_font)
        terms_label.SetForegroundColour(wx.Colour(33, 150, 243))
        self.results_sizer.Add(terms_label, 0, wx.ALL, 10)
        
        # Add separator
        line = wx.StaticLine(self.results_panel)
        self.results_sizer.Add(line, 0, wx.EXPAND | wx.ALL, 10)
        
        if not products or len(products) == 0:
            no_results = wx.StaticText(self.results_panel, label=f"No products found for '{search_terms}'")
            no_results_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            no_results.SetFont(no_results_font)
            no_results.SetForegroundColour(wx.Colour(128, 128, 128))
            self.results_sizer.Add(no_results, 0, wx.ALIGN_CENTER | wx.ALL, 50)
            self.results_panel.SetupScrolling()
            self.results_panel.Layout()
            return
        
        # Display products
        for i, product in enumerate(products):
            self.create_product_card(product)
        
        self.results_panel.SetupScrolling()
        self.results_panel.Layout()
    
    def on_search(self, event):
        """Handle product search (keeping old text search for compatibility)"""
        query = self.search_entry.GetValue().strip()
        
        if not query:
            wx.MessageBox("Please enter a product name", "Warning", wx.OK | wx.ICON_WARNING)
            return
        
        # Clear previous results
        self.results_sizer.Clear(True)
        
        # Show loading message
        loading = wx.StaticText(self.results_panel, label="Searching...")
        loading_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        loading.SetFont(loading_font)
        self.results_sizer.Add(loading, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        self.results_panel.Layout()
        
        # Search in background thread
        def search_thread():
            products = self.client.search_product(query)
            wx.CallAfter(self.display_results, products, query)
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def display_results(self, products, query):
        """Display search results"""
        # Clear loading message
        self.results_sizer.Clear(True)
        
        if not products:
            no_results = wx.StaticText(self.results_panel, label=f"No products found for '{query}'")
            no_results_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
            no_results.SetFont(no_results_font)
            no_results.SetForegroundColour(wx.Colour(128, 128, 128))
            self.results_sizer.Add(no_results, 0, wx.ALIGN_CENTER | wx.ALL, 50)
            self.results_panel.SetupScrolling()
            self.results_panel.Layout()
            return
        
        # Display products
        for i, product in enumerate(products):
            self.create_product_card(product)
        
        self.results_panel.SetupScrolling()
        self.results_panel.Layout()
    
    def create_product_card(self, product):
        """Create a card for each product"""
        # Card panel
        card = wx.Panel(self.results_panel, style=wx.BORDER_SIMPLE)
        card.SetBackgroundColour(wx.Colour(255, 255, 255))
        card_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Product name (clickable)
        name_label = wx.StaticText(card, label=product['name'])
        name_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        name_label.SetFont(name_font)
        name_label.SetForegroundColour(wx.Colour(33, 150, 243))
        name_label.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        name_label.Bind(wx.EVT_LEFT_DOWN, lambda e: webbrowser.open(product.get('product_link', '#')))
        card_sizer.Add(name_label, 0, wx.ALL, 5)
        
        # Price
        price_label = wx.StaticText(card, label=f"Price: {product['price']}")
        card_sizer.Add(price_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        # Source
        source_label = wx.StaticText(card, label=f"Source: {product['source']}")
        source_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        source_label.SetFont(source_font)
        source_label.SetForegroundColour(wx.Colour(128, 128, 128))
        card_sizer.Add(source_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        # Rating
        rating = product.get('rating', 0)
        reviews = product.get('reviews', 0)
        if rating:
            stars = "⭐" * int(rating)
            rating_label = wx.StaticText(card, label=f"{stars} ({reviews} reviews)")
            card_sizer.Add(rating_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        # Link to thumbnail
        thumbnail_url = product.get('thumbnail', '')
        if thumbnail_url:
            thumb_label = wx.StaticText(card, label="[View Image]")
            thumb_label.SetForegroundColour(wx.Colour(33, 150, 243))
            thumb_label.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            thumb_label.Bind(wx.EVT_LEFT_DOWN, lambda e: webbrowser.open(thumbnail_url))
            card_sizer.Add(thumb_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        card.SetSizer(card_sizer)
        self.results_sizer.Add(card, 0, wx.EXPAND | wx.ALL, 10)
    
    def on_logout(self, event):
        """Handle logout"""
        if self.client:
            self.client.logout()
            self.client.close()
        
        self.client = None
        self.session_id = None
        self.username = None
        
        wx.MessageBox("You have been logged out", "Logged Out", wx.OK | wx.ICON_INFORMATION)
        self.show_login_screen()


def main():
    app = wx.App()
    ShoppingGUI()
    app.MainLoop()


if __name__ == "__main__":
    main()
