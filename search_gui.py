"""
Search GUI module
Handles image selection and search interface
"""
import wx
import os
from base_gui import GUIConstants, GUIUtils


class SearchGUI:
    """Handles image search and upload functionality"""

    def __init__(self, main_frame):
        self.main_frame = main_frame
        self.image_path_label = None
        self.search_btn = None
        self.image_preview = None
        self.selected_image_path = None

    def create_search_panel(self):
        """Create image search section in main panel"""
        search_panel = wx.Panel(self.main_frame.main_panel)
        search_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        search_sizer = wx.BoxSizer(wx.VERTICAL)

        # Search label
        search_label = wx.StaticText(
            search_panel, label="Search Products by Image:")
        search_label_font = GUIUtils.create_styled_font(12, wx.FONTWEIGHT_BOLD)
        search_label.SetFont(search_label_font)
        search_label.SetForegroundColour(wx.Colour(0, 0, 0))
        search_sizer.Add(search_label, 0, wx.ALL, 8)

        # Image upload section
        upload_sizer = self._create_upload_section(search_panel)
        search_sizer.Add(upload_sizer, 0, wx.ALL, 5)

        # Image preview
        self.image_preview = wx.StaticBitmap(search_panel)
        search_sizer.Add(
            self.image_preview, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        search_panel.SetSizer(search_sizer)
        self.main_frame.main_sizer.Add(
            search_panel, 0, wx.EXPAND | wx.ALL, 10)

    def _create_upload_section(self, parent):
        """Create image upload buttons section"""
        upload_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Upload button
        upload_btn = wx.Button(parent, label="Select Image", size=(100, 30))
        upload_btn.SetBackgroundColour(wx.Colour(0, 102, 204))
        upload_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        upload_btn.SetFont(GUIUtils.create_styled_font(12, wx.FONTWEIGHT_BOLD))
        upload_btn.Bind(wx.EVT_BUTTON, self.main_frame.on_select_image)
        upload_sizer.Add(upload_btn, 0, wx.ALL, 5)

        # Camera button
        camera_btn = wx.Button(parent, label="Take Photo", size=(100, 30))
        camera_btn.SetBackgroundColour(wx.Colour(0, 102, 204))
        camera_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        camera_btn.SetFont(GUIUtils.create_styled_font(12, wx.FONTWEIGHT_BOLD))
        camera_btn.Bind(wx.EVT_BUTTON, self.main_frame.on_take_photo)
        upload_sizer.Add(camera_btn, 0, wx.ALL, 5)

        # Selected image label
        self.image_path_label = wx.StaticText(
            parent, label="No image selected")
        self.image_path_label.SetForegroundColour(wx.Colour(128, 128, 128))
        self.image_path_label.SetFont(GUIUtils.create_styled_font(10))
        upload_sizer.Add(
            self.image_path_label,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            5)

        # Search button (disabled until image is selected)
        self.search_btn = wx.Button(
            parent, label="Search by Image", size=(100, 30))
        self.search_btn.SetBackgroundColour(wx.Colour(0, 102, 204))
        self.search_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.search_btn.SetFont(
            GUIUtils.create_styled_font(12, wx.FONTWEIGHT_BOLD))
        self.search_btn.Bind(wx.EVT_BUTTON, self.main_frame.on_image_search)
        self.search_btn.Enable(False)
        upload_sizer.Add(self.search_btn, 0, wx.ALL, 5)

        return upload_sizer

    def select_image(self):
        """Handle image selection"""
        dialog = self._create_image_file_dialog()

        if dialog.ShowModal() == wx.ID_OK:
            self.selected_image_path = dialog.GetPath()
            self._update_image_selection()
            self._load_image_preview()

        dialog.Destroy()

    def _create_image_file_dialog(self):
        """Create file dialog for image selection"""
        exts = "*.jpg;*.jpeg;*.png;*.gif;*.webp"
        wildcard = f"Image files ({exts})|{exts}"

        return wx.FileDialog(
            self.main_frame,
            message="Choose an image file",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )

    def _update_image_selection(self):
        """Update UI after image is selected"""
        filename = os.path.basename(self.selected_image_path)
        self.image_path_label.SetLabel(f"Selected: {filename}")
        self.search_btn.Enable(True)

    def _load_image_preview(self):
        """Load and display image preview"""
        try:
            bitmap = GUIUtils.load_image_preview(self.selected_image_path)
            self.image_preview.SetBitmap(bitmap)
        except Exception as e:
            wx.MessageBox(
                f"Could not load image preview: {str(e)}",
                "Warning",
                wx.OK | wx.ICON_WARNING)

    def get_selected_image_path(self):
        """Return currently selected image path"""
        return self.selected_image_path

    def set_captured_image(self, image_path):
        """Set captured image from camera"""
        self.selected_image_path = image_path
        self._update_image_selection()
        self._load_image_preview()
