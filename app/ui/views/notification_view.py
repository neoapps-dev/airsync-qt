import os
import base64
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QPixmap, QIcon, QMouseEvent

from app.core.app_state import AppState
from app.model.notification import Notification


class NotificationView(QWidget):
    delete_notification_signal = Signal(Notification)
    hide_notification_signal = Signal(Notification)

    def __init__(self, notification: Notification = None):
        super().__init__()
        self.notification = notification
        self.app_state = AppState()
        self.setMouseTracking(True)
        self._start_pos_x = None
        self._original_pos_x = None
        self._swipe_threshold = 100
        self._animation = None
        self.setStyleSheet("""
            NotificationView {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            QLabel {
                color: #333333;
            }
            #dismissLabel {
                background-color: #ff3b30;
                color: white;
                padding: 5px;
                border-radius: 8px;
            }
            #hideLabel {
                background-color: #ff3b30;
                color: white;
                padding: 5px;
                border-radius: 8px;
            }
        """)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.content_container = QWidget(self)
        self.content_container.setLayout(self.main_layout)
        self.dismiss_label = QLabel("Dismiss", self)
        self.dismiss_label.setObjectName("dismissLabel")
        self.dismiss_label.setAlignment(Qt.AlignCenter)
        self.dismiss_label.hide()
        self.hide_label = QLabel("Dismiss", self)
        self.hide_label.setObjectName("hideLabel")
        self.hide_label.setAlignment(Qt.AlignCenter)
        self.hide_label.hide()
        self.overall_layout = QHBoxLayout(self)
        self.overall_layout.setContentsMargins(0, 0, 0, 0)
        self.overall_layout.addWidget(self.content_container)
        self.app_icon_label = QLabel()
        self.app_icon_label.setFixedSize(
            35, 35
        )
        self.update_app_icon()
        self.main_layout.addWidget(self.app_icon_label)
        self.text_layout = QVBoxLayout()
        self.text_layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel(f"{notification.app} - {notification.title}")
        self.title_label.setStyleSheet("font-weight: bold;")
        self.text_layout.addWidget(self.title_label)
        self.body_label = QLabel(notification.body)
        self.body_label.setWordWrap(True)
        self.text_layout.addWidget(self.body_label)
        self.main_layout.addLayout(self.text_layout)
        self.main_layout.addStretch()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.app_state.app_icons_changed.connect(self.update_app_icon)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._start_pos_x = event.globalPosition().x()
            self._original_pos_x = self.x()
            if self._animation and self._animation.state() == QPropertyAnimation.Running:
                self._animation.stop()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self._start_pos_x is not None:
            delta_x = event.globalPosition().x() - self._start_pos_x
            self.content_container.move(self._original_pos_x + delta_x, self.y())
            if delta_x > 0:
                self.dismiss_label.show()
                self.hide_label.hide()
                self.dismiss_label.setGeometry(self.content_container.x() - self.dismiss_label.width() - 10, self.y(), self.dismiss_label.width(), self.height())
            elif delta_x < 0:
                self.hide_label.show()
                self.dismiss_label.hide()
                self.hide_label.setGeometry(self.content_container.x() + self.content_container.width() + 10, self.y(), self.hide_label.width(), self.height())
            else:
                self.dismiss_label.hide()
                self.hide_label.hide()
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._start_pos_x is None:
            return

        swipe_distance = self.content_container.x() - self._original_pos_x

        if abs(swipe_distance) > self._swipe_threshold:
            if swipe_distance > 0:
                target_x = self.parentWidget().width()
                self._animate_widget(target_x, self.delete_notification_signal.emit)
            else:
                target_x = -self.width()
                self._animate_widget(target_x, self.hide_notification_signal.emit)
        else:
            self._animate_widget(self._original_pos_x)

        self._start_pos_x = None
        self.dismiss_label.hide()
        self.hide_label.hide()
        event.accept()

    def _animate_widget(self, target_x, on_finished_callback=None):
        self._animation = QPropertyAnimation(self.content_container, b"pos")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutQuad)
        self._animation.setStartValue(self.content_container.pos())
        self._animation.setEndValue(QPoint(target_x, self.content_container.y()))
        if on_finished_callback:
            self._animation.finished.connect(lambda: (on_finished_callback(self.notification), self.deleteLater()))
        else:
            self._animation.finished.connect(lambda: (self.dismiss_label.hide(), self.hide_label.hide()))

        self._animation.start()

    def update_app_icon(self):
        icon_path = self.app_state.app_icons.get(self.notification.package)
        print(f"Notification package: {self.notification.package}, Icon path present: {icon_path is not None}")
        if icon_path and os.path.exists(icon_path):
            try:
                pixmap = QPixmap(icon_path)
                self.app_icon_label.setPixmap(
                    pixmap.scaled(25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            except Exception as e:
                print(f"Error loading app icon from path {icon_path}: {e}")
                self.app_icon_label.setPixmap(
                    QIcon.fromTheme("application-x-executable").pixmap(25, 25)
                )
        else:
            self.app_icon_label.setPixmap(
                QIcon.fromTheme("application-x-executable").pixmap(25, 25)
            )


class NotificationListView(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.app_state.notifications_changed.connect(self.update_notification_list)
        self.update_notification_list(self.app_state.notifications)

    def update_notification_list(self, notifications):
        for i in reversed(range(self.main_layout.count())):
            widget = self.main_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not notifications:
            no_notifications_label = QLabel("No notifications yet.")
            no_notifications_label.setAlignment(Qt.AlignCenter)
            self.main_layout.addWidget(no_notifications_label)
        else:
            for notification in notifications:
                notification_widget = NotificationView(notification)
                notification_widget.delete_notification_signal.connect(self._handle_delete_notification)
                notification_widget.hide_notification_signal.connect(self._handle_hide_notification)
                self.main_layout.addWidget(notification_widget)

    def _handle_delete_notification(self, notification):
        self.app_state.remove_notification(notification)

    def _handle_hide_notification(self, notification):
        self.app_state.remove_notification_by_id(notification.nid)
