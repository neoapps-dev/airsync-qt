from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QColor

class GlassBoxView(QWidget):
    def __init__(self, color: QColor = QColor(128, 128, 128, int(0.2 * 255)), width: int = 0, height: int = 0, radius: int = 0):
        super().__init__()
        self.color = color
        self.radius = radius

        if width > 0 and height > 0:
            self.setFixedSize(width, height)

        self.setStyleSheet(f"""
            background-color: rgba({self.color.red()}, {self.color.green()}, {self.color.blue()}, {self.color.alpha()});
            border-radius: {self.radius}px;
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def add_widget(self, widget: QWidget):
        self.layout.addWidget(widget)

    def add_layout(self, layout):
        self.layout.addLayout(layout)