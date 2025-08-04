from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt

from app.core.app_state import AppState
from app.core.adb_connector import ADBConnector
from app.ui.views.phone_view import PhoneView

class SidebarView(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)

        self.phone_view = PhoneView()
        self.phone_view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.layout.addWidget(self.phone_view)
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(20, 0, 20, 20)
        self.mirror_button = QPushButton("Mirror")
        self.mirror_button.clicked.connect(self._mirror_action)
        self.button_layout.addWidget(self.mirror_button)
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self._disconnect_action)
        self.button_layout.addWidget(self.disconnect_button)
        self.layout.addLayout(self.button_layout)
        self.app_state.adb_connected_changed.connect(self._update_button_states)
        self._update_button_states()

    def _update_device_status_visibility(self):
        if self.app_state.status:
            self.device_status_view.setVisible(True)
        else:
            self.device_status_view.setVisible(False)

    def _update_button_states(self):
        self.mirror_button.setVisible(self.app_state.adb_connected)
        if self.app_state.adb_connected:
            self.disconnect_button.setText("Disconnect")
        else:
            self.disconnect_button.setText("Disconnect")

    def _mirror_action(self):
        if self.app_state.device:
            ADBConnector.start_scrcpy(
                ip=self.app_state.device.ip_address,
                port=self.app_state.adb_port,
                device_name=self.app_state.device.name,
                desktop=False)

    def _disconnect_action(self):
        self.app_state.disconnect_device()
        ADBConnector.disconnect_adb()
        self.app_state.adb_connected = False