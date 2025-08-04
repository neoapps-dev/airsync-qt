from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor

from app.core.app_state import AppState
from app.core.websocket_server import WebSocketServer


class MediaPlayerView(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(Qt.AlignCenter)
        self.title_label = QLabel("No Music Playing")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)
        self.artist_label = QLabel("")
        self.artist_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.artist_label)
        self.controls_layout = QHBoxLayout()
        self.prev_button = QPushButton(QIcon.fromTheme("media-skip-backward"), "")
        self.prev_button.clicked.connect(self._skip_previous)
        self.controls_layout.addWidget(self.prev_button)

        self.play_pause_button = QPushButton(
            QIcon.fromTheme("media-playback-start"), ""
        )
        self.play_pause_button.clicked.connect(self._toggle_play_pause)
        self.controls_layout.addWidget(self.play_pause_button)
        self.next_button = QPushButton(QIcon.fromTheme("media-skip-forward"), "")
        self.next_button.clicked.connect(self._skip_next)
        self.controls_layout.addWidget(self.next_button)
        self.layout.addLayout(self.controls_layout)
        self.app_state.status_changed.connect(self._update_media_player_ui)
        self._update_media_player_ui()

    def _update_media_player_ui(self):
        if self.app_state.status and self.app_state.status.music:
            music = self.app_state.status.music
            self.title_label.setText(music.title)
            self.artist_label.setText(music.artist)
            self.play_pause_button.setIcon(
                QIcon.fromTheme(
                    "media-playback-pause"
                    if music.is_playing
                    else "media-playback-start"
                )
            )
        else:
            self.title_label.setText("No Music Playing")
            self.artist_label.setText("")
            self.play_pause_button.setIcon(QIcon.fromTheme("media-playback-start"))

    def _toggle_play_pause(self):
        WebSocketServer().send_media_action("playPause")

    def _skip_next(self):
        WebSocketServer().send_media_action("next")

    def _skip_previous(self):
        WebSocketServer().send_media_action("previous")

    def set_text_color(self, brightness: int):
        if brightness > 180:
            color = QColor(Qt.black)
        else:
            color = QColor(Qt.white)
        self.title_label.setStyleSheet(f"color: {color.name()};")
        self.artist_label.setStyleSheet(f"color: {color.name()};")