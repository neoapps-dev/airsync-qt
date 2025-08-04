from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QDesktopServices

from app.core.app_state import AppState
from app.ui.views.notification_view import NotificationListView
from app.ui.views.settings_view import SettingsView


class AppContentView(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_widget = QTabWidget()
        self.notification_list_scroll_area = QScrollArea()
        self.notification_list_scroll_area.setWidgetResizable(True)
        self.notification_list_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.notification_view = NotificationListView()
        self.notification_list_scroll_area.setWidget(self.notification_view)
        self.settings_view = SettingsView()
        self.tab_widget.addTab(self.notification_list_scroll_area, "Notifications")
        self.tab_widget.addTab(self.settings_view, "Settings")
        self.tab_widget.tabBar().setExpanding(True)
        self.tab_widget.setStyleSheet("QTabBar::tab { text-align: center; }")
        self.main_layout.addWidget(self.tab_widget)
        self.feedback_layout = QHBoxLayout()
        self.feedback_layout.setAlignment(Qt.AlignRight)
        self.feedback_button = QPushButton("Feedback")
        self.feedback_button.setIcon(QIcon.fromTheme("dialog-information"))
        self.feedback_button.clicked.connect(self._open_feedback_link)
        self.feedback_layout.addWidget(self.feedback_button)
        self.main_layout.addLayout(self.feedback_layout)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.app_state.selected_tab_changed.connect(self._update_selected_tab)
        self._update_selected_tab(self.app_state.selected_tab)

    def _on_tab_changed(self, index):
        if index == 0:
            self.app_state.selected_tab = "Notifications"
        elif index == 1:
            self.app_state.selected_tab = "Settings"

    def _update_selected_tab(self, tab_name):
        if tab_name == "Notifications":
            self.tab_widget.setCurrentIndex(0)
        elif tab_name == "Settings":
            self.tab_widget.setCurrentIndex(1)

    def _open_feedback_link(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/neoapps-dev/airsync-qt/issues/new/choose")
        )
