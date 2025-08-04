from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from app.core.app_state import AppState

class BatteryStatusView(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignRight)
        self.battery_label = QLabel("N/A")
        self.layout.addWidget(self.battery_label)
        self.app_state.status_changed.connect(self._update_status)
        self._update_status()

    def _update_status(self):
        if self.app_state.status:
            battery = self.app_state.status.battery
            self.battery_label.setText(f"{battery.level}% {'⚡️' if battery.is_charging else ''}")
        else:
            self.battery_label.setText("N/A")

    def set_text_color(self, brightness):
        if brightness > 128:
            self.battery_label.setStyleSheet("color: black;")
        else:
            self.battery_label.setStyleSheet("color: white;")
