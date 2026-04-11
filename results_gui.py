"""
Results GUI module
Handles display of search results and product cards
"""
import wx
import wx.lib.scrolledpanel as scrolled
import webbrowser
from base_gui import GUIConstants, GUIUtils


class ResultsGUI:
    """Handles search results display"""

    def __init__(self, main_frame):
        self.main_frame = main_frame
        self.results_panel = None
        self.results_sizer = None

    def create_results_panel(self):
        """Create scrollable results display panel"""
        # Results label
        results_label = wx.StaticText(
            self.main_frame.main_panel, label="Results:")
        results_label_font = GUIUtils.create_styled_font(12, wx.FONTWEIGHT_BOLD)
        results_label.SetFont(results_label_font)
        results_label.SetForegroundColour(wx.Colour(0, 0, 0))
        self.main_frame.main_sizer.Add(results_label, 0,
                                       wx.LEFT | wx.RIGHT, 10)

        # Results panel with scrolling
        self.results_panel = scrolled.ScrolledPanel(
            self.main_frame.main_panel)
        self.results_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.results_panel.SetupScrolling()
        self.results_sizer = wx.BoxSizer(wx.VERTICAL)
        self.results_panel.SetSizer(self.results_sizer)
        self.main_frame.main_sizer.Add(
            self.results_panel, 1, wx.EXPAND | wx.ALL, 10)

    def show_initial_message(self):
        """Show initial message in results area"""
        self.results_sizer.Clear(True)

        msg = wx.StaticText(
            self.results_panel,
            label="Select an image to search for similar products...")
        msg_font = GUIUtils.create_styled_font(11)
        msg.SetFont(msg_font)
        msg.SetForegroundColour(wx.Colour(128, 128, 128))
        self.results_sizer.Add(msg, 0, wx.ALIGN_CENTER | wx.ALL, 30)

        self.results_panel.SetupScrolling()
        self.results_panel.Layout()

    def show_loading_message(self, message="Analyzing image and searching..."):
        """Show loading message"""
        self.results_sizer.Clear(True)

        loading = wx.StaticText(self.results_panel, label=message)
        loading_font = GUIUtils.create_styled_font(GUIConstants.HEADING_SIZE)
        loading.SetFont(loading_font)
        self.results_sizer.Add(loading, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        self.results_panel.Layout()

    def display_image_results(self, products, search_terms):
        """Display search results from image search"""
        self.results_sizer.Clear(True)

        # Check if there was an error
        if products is None:
            error_msg = wx.StaticText(
                self.results_panel,
                label=f"Error: {search_terms}")
            error_font = GUIUtils.create_styled_font(GUIConstants.HEADING_SIZE)
            error_msg.SetFont(error_font)
            error_msg.SetForegroundColour(GUIConstants.ERROR_COLOR)
            self.results_sizer.Add(error_msg, 0, wx.ALIGN_CENTER | wx.ALL, 50)
            self.results_panel.SetupScrolling()
            self.results_panel.Layout()
            return

        # Show extracted search terms
        terms_label = wx.StaticText(
            self.results_panel,
            label=f"AI detected: {search_terms}")
        terms_font = GUIUtils.create_styled_font(
            GUIConstants.NORMAL_SIZE,
            wx.FONTWEIGHT_BOLD,
            wx.FONTSTYLE_ITALIC)
        terms_label.SetFont(terms_font)
        terms_label.SetForegroundColour(GUIConstants.PRIMARY_COLOR)
        self.results_sizer.Add(terms_label, 0, wx.ALL, 10)

        # Add separator
        line = wx.StaticLine(self.results_panel)
        self.results_sizer.Add(line, 0, wx.EXPAND | wx.ALL, 10)

        if not products or len(products) == 0:
            no_results = wx.StaticText(
                self.results_panel,
                label=f"No products found for '{search_terms}'")
            no_results_font = GUIUtils.create_styled_font(GUIConstants.HEADING_SIZE)
            no_results.SetFont(no_results_font)
            no_results.SetForegroundColour(GUIConstants.GRAY_COLOR)
            self.results_sizer.Add(no_results, 0, wx.ALIGN_CENTER | wx.ALL, 50)
            self.results_panel.SetupScrolling()
            self.results_panel.Layout()
            return

        # Display products
        for product in products:
            self._create_product_card(product)

        self.results_panel.SetupScrolling()
        self.results_panel.Layout()

    def display_text_results(self, products, query):
        """Display search results from text search"""
        self.results_sizer.Clear(True)

        if not products:
            no_results = wx.StaticText(
                self.results_panel,
                label=f"No products found for '{query}'")
            no_results_font = GUIUtils.create_styled_font(GUIConstants.HEADING_SIZE)
            no_results.SetFont(no_results_font)
            no_results.SetForegroundColour(GUIConstants.GRAY_COLOR)
            self.results_sizer.Add(no_results, 0, wx.ALIGN_CENTER | wx.ALL, 50)
            self.results_panel.SetupScrolling()
            self.results_panel.Layout()
            return

        # Display products
        for product in products:
            self._create_product_card(product)

        self.results_panel.SetupScrolling()
        self.results_panel.Layout()

    def _create_product_card(self, product):
        """Create a card for each product"""
        # Card panel
        card = wx.Panel(self.results_panel, style=wx.BORDER_SIMPLE)
        card.SetBackgroundColour(GUIConstants.WHITE)
        card_sizer = wx.BoxSizer(wx.VERTICAL)

        # Product name (clickable)
        name_label = wx.StaticText(card, label=product['name'])
        name_font = GUIUtils.create_styled_font(
            GUIConstants.NORMAL_SIZE,
            wx.FONTWEIGHT_BOLD)
        name_label.SetFont(name_font)
        name_label.SetForegroundColour(GUIConstants.PRIMARY_COLOR)
        name_label.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        name_label.Bind(
            wx.EVT_LEFT_DOWN,
            lambda e: webbrowser.open(
                product.get(
                    'product_link',
                    '#')))
        card_sizer.Add(name_label, 0, wx.ALL, 5)

        # Price
        price_label = wx.StaticText(card, label=f"Price: {product['price']}")
        card_sizer.Add(price_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Source
        source_label = wx.StaticText(
            card, label=f"Source: {product['source']}")
        source_font = GUIUtils.create_styled_font(GUIConstants.SMALL_SIZE)
        source_label.SetFont(source_font)
        source_label.SetForegroundColour(GUIConstants.GRAY_COLOR)
        card_sizer.Add(source_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Rating
        rating = product.get('rating', 0)
        reviews = product.get('reviews', 0)
        if rating:
            stars = "★" * int(rating)
            rating_label = wx.StaticText(
                card, label=f"{stars} ({reviews} reviews)")
            card_sizer.Add(rating_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Link to thumbnail
        thumbnail_url = product.get('thumbnail', '')
        if thumbnail_url:
            thumb_label = wx.StaticText(card, label="[View Image]")
            thumb_label.SetForegroundColour(GUIConstants.PRIMARY_COLOR)
            thumb_label.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            thumb_label.Bind(wx.EVT_LEFT_DOWN,
                             lambda e: webbrowser.open(thumbnail_url))
            card_sizer.Add(thumb_label, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        card.SetSizer(card_sizer)
        self.results_sizer.Add(card, 0, wx.EXPAND | wx.ALL, 10)
