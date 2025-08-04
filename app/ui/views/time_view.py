from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

from datetime import datetime

class TimeView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)
        self.time_label = QLabel()
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.time_label.setFont(font)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.time_label)
        self.date_label = QLabel()
        font = QFont()
        font.setPointSize(12)
        self.date_label.setFont(font)
        self.date_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.date_label)
        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        current_time = datetime.now()
        self.time_label.setText(current_time.strftime("%H:%M"))
        self.date_label.setText(current_time.strftime("%A, %B %d"))

    def set_text_color(self, brightness: int):
        if brightness > 180:
            color = QColor(Qt.black)
        else:
            color = QColor(Qt.white)
        self.time_label.setStyleSheet(f"color: {color.name()};")
        self.date_label.setStyleSheet(f"color: {color.name()};")
