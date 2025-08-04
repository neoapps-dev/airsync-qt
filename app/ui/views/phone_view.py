from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap

from app.core.app_state import AppState
from app.ui.views.screen_view import ScreenView

class PhoneView(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.outer_frame = QWidget()
        self.outer_frame.setFixedSize(220, 450)
        self.outer_frame.setStyleSheet("background-color: #222; border-radius: 30px;")
        self.outer_layout = QVBoxLayout(self.outer_frame)
        self.outer_layout.setContentsMargins(10, 10, 10, 10)
        self.screen_view = ScreenView()
        self.screen_view.setFixedSize(200, 400)
        self.outer_layout.addWidget(self.screen_view)
        self.main_layout.addWidget(self.outer_frame)

    def sizeHint(self):
        return QSize(220, 450)

    def minimumSizeHint(self):
        return QSize(220, 450)
