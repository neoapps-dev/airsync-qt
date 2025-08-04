from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from app.core.app_state import AppState

class DeviceStatusView(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.battery_label = QLabel("Battery: N/A")
        self.music_label = QLabel("Music: N/A")
        self.layout.addWidget(self.battery_label)
        self.layout.addWidget(self.music_label)
        self.app_state.status_changed.connect(self._update_status)
        self._update_status()

    def _update_status(self):
        if self.app_state.status:
            battery = self.app_state.status.battery
            music = self.app_state.status.music

            self.battery_label.setText(f"Battery: {battery.level}% {'⚡️ Charging' if battery.is_charging else ''}")
            self.music_label.setText(f"Music: {music.title} by {music.artist} (Playing: {music.is_playing})")
        else:
            self.battery_label.setText("Battery: N/A")
            self.music_label.setText("Music: N/A")