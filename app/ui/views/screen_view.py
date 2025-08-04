from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QImage, QColor
from pathlib import Path

from app.core.app_state import AppState
from app.ui.views.time_view import TimeView
from app.ui.views.media_player_view import MediaPlayerView
from app.ui.views.battery_status_view import BatteryStatusView

class ScreenView(QWidget):
    background_brightness_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self._wallpaper_pixmap = None
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)
        self.status_bar = QWidget()
        self.status_bar.setStyleSheet("background-color: transparent;")
        self.status_bar_layout = QHBoxLayout(self.status_bar)
        self.status_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.status_bar_layout.addStretch()
        self.battery_status_view = BatteryStatusView()
        self.status_bar_layout.addWidget(self.battery_status_view)
        self.layout.addWidget(self.status_bar)
        self.time_view = TimeView()
        self.time_view.setStyleSheet("background-color: transparent;")
        self.layout.addWidget(self.time_view)
        self.layout.addStretch()
        self.media_player_view = MediaPlayerView()
        self.media_player_view.setStyleSheet("background-color: transparent;")
        self.layout.addWidget(self.media_player_view)
        self.app_state.device_wallpapers_changed.connect(self._update_wallpaper)
        self._update_wallpaper()
        self.background_brightness_changed.connect(self.time_view.set_text_color)
        self.background_brightness_changed.connect(self.media_player_view.set_text_color)
        self.background_brightness_changed.connect(self.battery_status_view.set_text_color)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self._wallpaper_pixmap:
            scaled_pixmap = self._wallpaper_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled_pixmap.width()) / 2
            y = (self.height() - scaled_pixmap.height()) / 2
            painter.drawPixmap(x, y, scaled_pixmap)
        else:
            painter.fillRect(self.rect(), Qt.black)

        super().paintEvent(event)

    def _update_wallpaper(self):
        wallpaper_path = self.app_state.current_wallpaper_path
        print(f"Updating wallpaper with path: {wallpaper_path}")
        if wallpaper_path and Path(wallpaper_path).exists():
            self._wallpaper_pixmap = QPixmap(wallpaper_path)
        else:
            self._wallpaper_pixmap = QPixmap("app/resources/wallpaper.jpg")
        self.update()
        self._emit_brightness_signal()

    def _calculate_brightness(self, pixmap: QPixmap) -> int:
        scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image = scaled_pixmap.toImage()
        if image.isNull():
            return 0

        total_brightness = 0
        pixel_count = 0

        for y in range(image.height()):
            for x in range(image.width()):
                pixel_color = QColor(image.pixel(x, y))
                luminance = (0.299 * pixel_color.red() + 0.587 * pixel_color.green() + 0.114 * pixel_color.blue())
                total_brightness += luminance
                pixel_count += 1

        if pixel_count > 0:
            return int(total_brightness / pixel_count)
        return 0

    def _emit_brightness_signal(self):
        if self._wallpaper_pixmap:
            brightness = self._calculate_brightness(self._wallpaper_pixmap)
            self.background_brightness_changed.emit(brightness)
