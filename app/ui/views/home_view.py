from PySide6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget

from app.core.app_state import AppState
from app.ui.views.scanner_view import ScannerView
from app.ui.views.sidebar_view import SidebarView
from app.ui.views.app_content_view import AppContentView

class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.left_panel_stacked_widget = QStackedWidget()
        self.sidebar_view = SidebarView()
        self.scanner_view = ScannerView()
        self.left_panel_stacked_widget.addWidget(self.scanner_view)
        self.left_panel_stacked_widget.addWidget(self.sidebar_view)
        self.app_content_view = AppContentView()
        self.main_layout.addWidget(self.left_panel_stacked_widget, 1)
        self.main_layout.addWidget(self.app_content_view, 3)
        self.app_state.device_changed.connect(self.update_view_based_on_device)
        self.update_view_based_on_device(self.app_state.device)

    def update_view_based_on_device(self, device):
        if device:
            self.left_panel_stacked_widget.setCurrentWidget(self.sidebar_view)
        else:
            self.left_panel_stacked_widget.setCurrentWidget(self.scanner_view)
