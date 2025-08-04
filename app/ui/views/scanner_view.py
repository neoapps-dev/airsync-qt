import qrcode

from urllib.parse import quote_plus
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os
from pathlib import Path
from app.core.app_state import AppState


class ScannerView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("color: white;")
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
        self.qr_image_label = QLabel()
        self.qr_image_label.setAlignment(Qt.AlignCenter)
        self.qr_image_label.setFixedSize(190, 190)
        self.qr_image_label.setStyleSheet(
            "background-color: white; border-radius: 20px;"
        )
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.main_layout.addWidget(QLabel("Scan to connect", alignment=Qt.AlignCenter))
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.qr_image_label)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.status_label)
        self.app_state = AppState()
        self.app_state.websocket_status_changed.connect(self.update_status_display)
        self.app_state.should_refresh_qr_changed.connect(self.handle_refresh_qr)
        self.generate_qr_async()
        self.update_status_display(self.app_state.websocket_status)

    def status_info(self, status):
        if "stopped" in status:
            return "Stopped", "#808080"
        elif "starting" in status:
            return "Starting...", "#FFA500"
        elif "started" in status:
            return "Ready", "#008000"
        elif "failed" in status:
            return f"Failed: {status.split(':', 1)[1].strip()}", "#FF0000"
        return "Unknown", "#808080"

    def update_status_display(self, status):
        text, color = self.status_info(status)
        self.status_label.setText(text)

    def generate_qr_async(self):
        ip = self.app_state.get_local_ip_address()
        port = self.app_state.my_device.port if self.app_state.my_device else 6996
        name = self.app_state.my_device.name if self.app_state.my_device else "Unknown"
        print(f"DEBUG: QR generation - IP: {ip}, Port: {port}, Name: {name}")
        qr_text = self.generate_qr_text(ip, port, name)
        print(f"DEBUG: QR text: {qr_text}")
        if qr_text:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=5,
                    border=2,
                )
                qr.add_data(qr_text)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img_path = os.path.expanduser("~/.airsync/qr_code.png")
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                img.save(img_path)
                pixmap = QPixmap(img_path)
                self.qr_image_label.setPixmap(
                    pixmap.scaled(190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
            except Exception as e:
                print(f"QR generation failed: {e}")
                self.qr_image_label.setText("Error generating QR")
        else:
            self.qr_image_label.setText("Cannot generate QR")

    def generate_qr_text(self, ip: str, port: int, name: str) -> str:
        if not ip or not port:
            return ""
        encoded_name = quote_plus(name)
        plus_value = str(self.app_state.is_plus).lower()
        return f"airsync://{ip}:{port}?name={encoded_name}?plus={plus_value}"

    def handle_refresh_qr(self, value):
        if value:
            self.generate_qr_async()
            self.app_state.should_refresh_qr = False
