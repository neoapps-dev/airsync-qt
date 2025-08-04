from PySide6.QtWidgets import QPushButton, QVBoxLayout, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QSize

class GlassButtonView(QPushButton):
    def __init__(self, label: str, system_image: str, icon_only: bool = False, action=None):
        super().__init__()
        self.label_text = label
        self.system_image = system_image
        self.icon_only = icon_only
        self.setFixedSize(100, 60)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(128, 128, 128, 0.2);
                border-radius: 15px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(128, 128, 128, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(128, 128, 128, 0.4);
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(5, 5, 5, 5)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.icon_label)

        if not self.icon_only:
            self.text_label = QLabel(self.label_text)
            self.text_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(self.text_label)

        self.update_icon()

        if action:
            self.clicked.connect(action)

    def update_icon(self):
        icon_name_map = {
            "apps.iphone": "smartphone",
            "xmark": "close",
            "checkmark.circle": "check",
            "play.circle": "play",
            "stop.circle": "stop",
            "link": "link",
            "square.and.arrow.down.badge.checkmark": "save"
        }
        icon_theme_name = icon_name_map.get(self.system_image, "dialog-information")
        icon = QIcon.fromTheme(icon_theme_name)
        if not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(QSize(32, 32)))
        else:
            self.icon_label.setText("❓")

    def setIconOnly(self, icon_only: bool):
        self.icon_only = icon_only
        if hasattr(self, 'text_label'):
            self.text_label.setVisible(not icon_only)
        self.update_icon()

    def setText(self, text: str):
        self.label_text = text
        if hasattr(self, 'text_label'):
            self.text_label.setText(text)

    def setSystemImage(self, system_image: str):
        self.system_image = system_image
        self.update_icon()