from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QSlider, QGroupBox, QFormLayout, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QIntValidator

from app.core.websocket_server import WebSocketServer
from app.core.app_state import AppState
from app.core.adb_connector import ADBConnector
from app.model.license_details import LicenseDetails
from app.core.gumroad import check_license_key_validity

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.app_state = AppState()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setFocusPolicy(Qt.StrongFocus)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.device_name_group = QGroupBox("Device Name")
        self.device_name_layout = QHBoxLayout(self.device_name_group)
        self.device_name_label = QLabel("Device Name:")
        self.device_name_input = QLineEdit()
        self.device_name_input.setText(self.app_state.device_name)
        self.device_name_input.textChanged.connect(self._on_device_name_changed)
        self.device_name_layout.addWidget(self.device_name_label)
        self.device_name_layout.addWidget(self.device_name_input)
        self.scroll_layout.addWidget(self.device_name_group)
        self.adb_group = QGroupBox("ADB Settings")
        self.adb_layout = QVBoxLayout(self.adb_group)
        self.adb_enabled_layout = QHBoxLayout()
        self.adb_enabled_label = QLabel("Connect ADB:")
        self.adb_enabled_checkbox = QCheckBox()
        self.adb_enabled_checkbox.setChecked(self.app_state.adb_enabled)
        self.adb_enabled_checkbox.stateChanged.connect(self._on_adb_enabled_changed)
        self.adb_enabled_layout.addWidget(self.adb_enabled_label)
        self.adb_enabled_layout.addStretch()
        self.adb_enabled_layout.addWidget(self.adb_enabled_checkbox)
        self.adb_layout.addLayout(self.adb_enabled_layout)
        self.adb_port_layout = QHBoxLayout()
        self.adb_port_label = QLabel("ADB Port:")
        self.adb_port_input = QLineEdit()
        self.adb_port_input.setFixedWidth(100)
        self.adb_port_input.setText(str(self.app_state.adb_port))
        self.adb_port_input.textChanged.connect(self._on_adb_port_changed)
        self.adb_port_input.setValidator(QIntValidator(1, 65535, self))
        self.adb_connect_button = QPushButton("Connect ADB")
        self.adb_connect_button.clicked.connect(self._on_adb_connect_clicked)
        self.adb_disconnect_button = QPushButton("Disconnect ADB")
        self.adb_disconnect_button.clicked.connect(self._on_adb_disconnect_clicked)
        self.adb_port_layout.addWidget(self.adb_port_label)
        self.adb_port_layout.addWidget(self.adb_port_input)
        self.adb_port_layout.addWidget(self.adb_connect_button)
        self.adb_port_layout.addWidget(self.adb_disconnect_button)
        self.adb_port_layout.addStretch()
        self.adb_layout.addLayout(self.adb_port_layout)
        self.mirroring_plus_layout = QHBoxLayout()
        self.mirroring_plus_label = QLabel("App Mirroring:")
        self.mirroring_plus_checkbox = QCheckBox()
        self.mirroring_plus_checkbox.setChecked(self.app_state.mirroring_plus)
        self.mirroring_plus_checkbox.stateChanged.connect(self._on_mirroring_plus_changed)
        self.mirroring_plus_layout.addWidget(self.mirroring_plus_label)
        self.mirroring_plus_layout.addStretch()
        self.mirroring_plus_layout.addWidget(self.mirroring_plus_checkbox)
        self.adb_layout.addLayout(self.mirroring_plus_layout)
        self.scroll_layout.addWidget(self.adb_group)
        self.sync_group = QGroupBox("Sync Options")
        self.sync_layout = QVBoxLayout(self.sync_group)
        self.sync_status_layout = QHBoxLayout()
        self.sync_status_label = QLabel("Sync device status:")
        self.sync_status_checkbox = QCheckBox()
        self.sync_status_checkbox.setChecked(False)
        self.sync_status_checkbox.setEnabled(False)
        self.sync_status_layout.addWidget(self.sync_status_label)
        self.sync_status_layout.addStretch()
        self.sync_status_layout.addWidget(self.sync_status_checkbox)
        self.sync_layout.addLayout(self.sync_status_layout)
        self.sync_clipboard_layout = QHBoxLayout()
        self.sync_clipboard_label = QLabel("Sync clipboard:")
        self.sync_clipboard_checkbox = QCheckBox()
        self.sync_clipboard_checkbox.setChecked(self.app_state.is_clipboard_sync_enabled)
        self.sync_clipboard_checkbox.stateChanged.connect(self._on_clipboard_sync_changed)
        self.sync_clipboard_layout.addWidget(self.sync_clipboard_label)
        self.sync_clipboard_layout.addStretch()
        self.sync_clipboard_layout.addWidget(self.sync_clipboard_checkbox)
        self.sync_layout.addLayout(self.sync_clipboard_layout)
        self.scroll_layout.addWidget(self.sync_group)
        self.connection_info_group = QGroupBox("Connection Info")
        self.connection_info_layout = QFormLayout(self.connection_info_group)
        self.ip_address_label = QLabel(self.app_state.get_local_ip_address() or "N/A")
        self.connection_info_layout.addRow("IP Address:", self.ip_address_label)
        self.server_port_input = QLineEdit()
        self.server_port_input.setFixedWidth(100)
        self.server_port_input.setText(str(self.app_state.port))
        self.server_port_input.textChanged.connect(self._on_server_port_changed)
        self.server_port_input.setValidator(QIntValidator(1, 65535, self))
        self.connection_info_layout.addRow("Server Port:", self.server_port_input)
        self.plus_features_label = QLabel("Not active")
        self.connection_info_layout.addRow("Plus features:", self.plus_features_label)
        self.scroll_layout.addWidget(self.connection_info_group)
        self.save_restart_button = QPushButton("Save and Restart the Server")
        self.save_restart_button.clicked.connect(self._on_save_restart_clicked)
        self.scroll_layout.addWidget(self.save_restart_button)
        self.opacity_layout = QHBoxLayout()
        self.opacity_label = QLabel("Window Opacity:")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self.app_state.window_opacity * 100))
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        self.opacity_value_label = QLabel(f"{int(self.app_state.window_opacity * 100)}%")
        self.opacity_layout.addWidget(self.opacity_label)
        self.opacity_layout.addWidget(self.opacity_slider)
        self.opacity_layout.addWidget(self.opacity_value_label)
        self.scroll_layout.addLayout(self.opacity_layout)
        self.license_group = QGroupBox("AirSync+")
        self.license_layout = QVBoxLayout(self.license_group)
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("Enter license key")
        self.license_layout.addWidget(self.license_key_input)
        self.license_buttons_layout = QHBoxLayout()
        self.check_license_button = QPushButton("Check License")
        self.check_license_button.clicked.connect(self._on_check_license_clicked)
        self.license_buttons_layout.addWidget(self.check_license_button)
        self.license_status_label = QLabel()
        self.license_buttons_layout.addWidget(self.license_status_label)
        self.get_plus_button = QPushButton("Get AirSync+")
        self.get_plus_button.clicked.connect(self._on_get_plus_clicked)
        self.license_buttons_layout.addWidget(self.get_plus_button)
        self.license_layout.addLayout(self.license_buttons_layout)
        self.license_details_widget = QWidget()
        self.license_details_layout = QFormLayout(self.license_details_widget)
        self.license_details_widget.setVisible(False)
        self.ld_email = QLabel()
        self.ld_product = QLabel()
        self.ld_order = QLabel()
        self.ld_purchaser_id = QLabel()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._on_apply_clicked)
        self.license_details_layout.addRow("Email:", self.ld_email)
        self.license_details_layout.addRow("Product:", self.ld_product)
        self.license_details_layout.addRow("Order #:", self.ld_order)
        self.license_details_layout.addRow("Purchaser ID:", self.ld_purchaser_id)
        self.license_details_layout.addWidget(self.apply_button)
        self.license_layout.addWidget(self.license_details_widget)
        self.scroll_layout.addWidget(self.license_group)
        self.why_plus_group = QGroupBox("Why plus?")
        self.why_plus_layout = QVBoxLayout(self.why_plus_group)
        self.why_plus_text = QLabel(
            """
Keeps me inspired to continue and maybe even to publish to the Apple app store and google play store. Think of it as a little donation to keep this project alive and evolving.
That said, I know not everyone who wants the full experience can afford it. If that’s you, please don’t hesitate to reach out. 😊

The source code is available on GitHub, and you're more than welcome to build with all Plus features free—for personal use which also opens for contributions which is a win win!.
As a thank-you for supporting the app, AirSync+ unlocks some nice extras: media controls, synced widgets, low battery alerts, wireless ADB, and more to come as I keep adding new features.

Enjoy the app!
(っ◕‿◕)っ
"""
        )
        self.why_plus_text.setWordWrap(True)
        self.why_plus_layout.addWidget(self.why_plus_text)
        self.scroll_layout.addWidget(self.why_plus_group)
        self.main_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_layout.addStretch(1)
        self._update_adb_ui_state()
        self._update_plus_features_label()
        self._update_license_details_ui()
        self.app_state.adb_enabled_changed.connect(self._update_adb_ui_state)
        self.app_state.adb_connected_changed.connect(self._update_adb_ui_state)
        self.app_state.is_plus_changed.connect(self._update_plus_features_label)
        self.app_state.window_opacity_changed.connect(self._update_opacity_label)
        self.app_state.is_clipboard_sync_enabled_changed.connect(self._update_clipboard_sync_checkbox)
        self.app_state.license_details_changed.connect(self._update_license_details_ui)
        self.setTabOrder(self.device_name_input, self.adb_port_input)
        self.setTabOrder(self.adb_port_input, self.server_port_input)
        self.setTabOrder(self.server_port_input, self.license_key_input)
        self.setTabOrder(self.license_key_input, self.check_license_button)
        self.setTabOrder(self.check_license_button, self.get_plus_button)
        self.setTabOrder(self.get_plus_button, self.save_restart_button)
        self.app_state.license_details_changed.connect(self._update_license_details_ui)

    def _on_device_name_changed(self, text):
        self.app_state.device_name = text

    def _on_adb_enabled_changed(self, state):
        self.app_state.adb_enabled = state == Qt.Checked
        self._update_adb_ui_state()

    def _update_adb_ui_state(self):
        is_adb_enabled = self.app_state.adb_enabled
        is_adb_connected = self.app_state.adb_connected
        self.adb_port_label.setVisible(is_adb_enabled)
        self.adb_port_input.setVisible(is_adb_enabled)
        self.adb_connect_button.setVisible(is_adb_enabled)
        self.adb_disconnect_button.setVisible(is_adb_enabled)
        self.adb_connect_button.setEnabled(is_adb_enabled and not is_adb_connected)
        self.adb_disconnect_button.setEnabled(is_adb_enabled and is_adb_connected)

    def _on_adb_port_changed(self, text):
        try:
            port = int(text)
            if 1 <= port <= 65535:
                self.app_state.adb_port = port
        except ValueError:
            pass

    def _on_adb_connect_clicked(self):
        ADBConnector.connect(self.app_state.adb_port)

    def _on_adb_disconnect_clicked(self):
        ADBConnector.disconnect()

    def _on_mirroring_plus_changed(self, state):
        self.app_state.mirroring_plus = state == Qt.Checked

    def _on_clipboard_sync_changed(self, state):
        self.app_state.is_clipboard_sync_enabled = state == Qt.Checked
        print(f"Clipboard sync enabled: {self.app_state.is_clipboard_sync_enabled}")

    def _on_server_port_changed(self, text):
        try:
            port = int(text)
            if 1 <= port <= 65535:
                self.app_state.port = port
        except ValueError:
            pass

    def _on_save_restart_clicked(self):
        self.app_state.save_settings()
        from app.main import AirSyncApp
        app = AirSyncApp.instance()
        if app:
            app.restart_websocket_server()
        QMessageBox.information(self, "Settings Saved", "Settings saved. Server will restart.")

    def _on_opacity_changed(self, value):
        self.app_state.window_opacity = value / 100.0
        self.opacity_value_label.setText(f"{value}%")

    def _on_check_license_clicked(self):
        license_key = self.license_key_input.text()
        license_details = check_license_key_validity(license_key)
        if license_details:
            self.app_state.is_plus = True
            self.license_status_label.setText("License Valid!")
            self.app_state.license_details = license_details
        else:
            self.app_state.is_plus = False
            self.license_status_label.setText("Invalid License Key")
            self.app_state.license_details = None
        self._update_license_details_ui()

    def _on_get_plus_clicked(self):
        QDesktopServices.openUrl(QUrl("https://airsync.sameerasw.com/"))

    def _on_apply_clicked(self):
        self.app_state.save_settings()
        QMessageBox.information(self, "Settings Applied", "Your settings have been saved.")

    def _update_plus_features_label(self):
        if self.app_state.is_plus:
            self.plus_features_label.setText("Active")
        else:
            self.plus_features_label.setText("Not active")

    def _update_opacity_label(self, opacity):
        self.opacity_value_label.setText(f"{int(opacity * 100)}%")

    def _update_clipboard_sync_checkbox(self, enabled):
        self.sync_clipboard_checkbox.setChecked(enabled)

    def _update_license_details_ui(self):
        if self.app_state.license_details:
            details = self.app_state.license_details
            self.ld_email.setText(details.email)
            self.ld_product.setText(details.product_name)
            self.ld_order.setText(details.order_number)
            self.ld_purchaser_id.setText(details.purchaser_id)
            self.license_details_widget.setVisible(True)
        else:
            self.license_details_widget.setVisible(False)
            self.ld_email.clear()
            self.ld_product.clear()
            self.ld_order.clear()
            self.ld_purchaser_id.clear()
