import json
import socket
from pathlib import Path
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QGuiApplication
import base64
from uuid import uuid4
from dataclasses import asdict
from desktop_notifier import DesktopNotifier
from desktop_notifier.common import Icon

from app.model.device import Device
from app.model.notification import Notification
from app.constants import Defaults
from app.model.license_details import LicenseDetails


class AppState(QObject):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            super().__init__()
            self._initialized = True

            self.device = None
            self.notifications = []
            self.status = None
            self.app_icons = {}
            self.device_wallpapers = {}
            self.current_device_wallpaper_base64 = None
            self.should_skip_save = False
            self.device_name = socket.gethostname()
            self.port = Defaults.server_port
            self.adb_port = Defaults.adb_port
            self.mirroring_plus = False
            self.adb_enabled = False
            self.is_clipboard_sync_enabled = False
            self.window_opacity = 1.0
            self.is_plus = False
            self.license_details = None
            print(f"AppState initialized. is_clipboard_sync_enabled: {self.is_clipboard_sync_enabled}")
            self.load_settings()
            self.load_cached_wallpapers()
            self.my_device = Device(
                name=self.device_name,
                ip_address=self.get_local_ip_address() or "N/A",
                port=self.port,
            )

            self.adb_connection_result = None
            self.should_refresh_qr = False
            self.websocket_status = "stopped"
            self._selected_tab = "settings"
            self.adb_connected = False

    @property
    def selected_tab(self) -> str:
        return self._selected_tab

    @selected_tab.setter
    def selected_tab(self, value: str):
        if self._selected_tab != value:
            self._selected_tab = value
            self.selected_tab_changed.emit(value)
            self.license_check = True

            self.clipboard_timer = QTimer(self)
            self.clipboard_timer.timeout.connect(self.check_clipboard)
            if self.is_clipboard_sync_enabled:
                self.start_clipboard_monitoring()
            self.post_native_notification(
                id="test_notification",
                app_name="AirSync Beta",
                title="Hi there! (っ◕‿◕)っ",
                body="Welcome to and thanks for testing out the app. Please don't forget to report issues to sameerasw.com@gmail.com or any other community you prefer. <3",
                app_icon=None
            )

    device_changed = Signal(Device)
    notifications_changed = Signal(list)
    status_changed = Signal()
    my_device_changed = Signal(Device)
    port_changed = Signal(int)
    app_icons_changed = Signal()
    device_wallpapers_changed = Signal()
    is_clipboard_sync_enabled_changed = Signal(bool)
    should_refresh_qr_changed = Signal(bool)
    websocket_status_changed = Signal(str)
    selected_tab_changed = Signal(str)
    adb_connected_changed = Signal(bool)
    license_details_changed = Signal()
    adb_port_changed = Signal(int)
    adb_connection_result_changed = Signal(str)
    mirroring_plus_changed = Signal(bool)
    adb_enabled_changed = Signal(bool)
    window_opacity_changed = Signal(float)
    is_plus_changed = Signal(bool)

    def load_settings(self):
        settings_path = self.get_settings_path()
        if settings_path.exists():
            try:
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                    self.device_name = settings.get("device_name", self.device_name)
                    self.port = settings.get("port", self.port)
                    self.adb_port = settings.get("adb_port", self.adb_port)
                    self.mirroring_plus = settings.get("mirroring_plus", self.mirroring_plus)
                    self.adb_enabled = settings.get("adb_enabled", self.adb_enabled)
                    self.is_clipboard_sync_enabled = settings.get(
                        "is_clipboard_sync_enabled", self.is_clipboard_sync_enabled
                    )
                    print(f"Loaded settings. is_clipboard_sync_enabled: {self.is_clipboard_sync_enabled}")
                    self.window_opacity = settings.get("window_opacity", self.window_opacity)
                    self.is_plus = settings.get("is_plus", self.is_plus)
                    license_details_dict = settings.get("license_details")
                    if license_details_dict:
                        self.license_details = LicenseDetails(**license_details_dict)
            except json.JSONDecodeError:
                print("Error reading settings.json. File might be corrupted. Using default settings.")
                self.save_settings()

    def save_settings(self):
        settings_path = self.get_settings_path()
        settings = {
            "device_name": self.device_name,
            "port": self.port,
            "adb_port": self.adb_port,
            "mirroring_plus": self.mirroring_plus,
            "adb_enabled": self.adb_enabled,
            "is_clipboard_sync_enabled": self.is_clipboard_sync_enabled,
            "window_opacity": self.window_opacity,
            "is_plus": self.is_plus,
            "license_details": asdict(self.license_details) if self.license_details else None,
            "app_icons": self.app_icons,
            "device_wallpaper": self.device_wallpapers,
        }
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=4)

    def get_settings_path(self):
        return Path.home() / ".airsync" / "settings.json"

    def get_local_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None

    def add_notification(self, notification: Notification):
        self.notifications.insert(0, notification)
        self.notifications_changed.emit(self.notifications)

    def remove_notification(self, notif: Notification):
        self.remove_notification_by_id(notif.nid)

    def remove_notification_by_id(self, nid: str):
        from app.core.websocket_server import WebSocketServer
        self.notifications = [n for n in self.notifications if n.nid != nid]
        self.notifications_changed.emit(self.notifications)
        WebSocketServer().dismiss_notification(nid)

    def hide_notification(self, notif: Notification):
        self.notifications = [n for n in self.notifications if n.id != notif.id]
        self.notifications_changed.emit(self.notifications)
        self.remove_notification(notif)

    def clear_notifications(self):
        if self.notifications:
            self.notifications.clear()
            self.notifications_changed.emit(self.notifications)

    async def post_native_notification(self, id: str, app_name: str, title: str, body: str, app_icon=None, package: str = None):
        icon_path = None
        if package and self.app_icons.get(package):
            icon_path = self.app_icons[package]

        app_icon_obj = Icon(path=Path(icon_path)) if icon_path else None
        notifier = DesktopNotifier(app_name=app_name, app_icon=app_icon_obj, notification_limit=10)
        await notifier.send(title=title, message=body)

    def sync_with_system_notifications(self):
        # TODO
        pass

    def wallpaper_cache_directory(self) -> Path:
        cache_dir = Path.home() / ".airsync" / "wallpapers"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def load_cached_wallpapers(self):
        wallpaper_dir = self.wallpaper_cache_directory()
        for file in wallpaper_dir.iterdir():
            if file.is_file():
                key = file.stem
                self.device_wallpapers[key] = str(file)

    def save_wallpaper_from_base64(self, base64_string: str):
        if not self.device:
            return

        key = f"{self.device.name}-{self.device.ip_address}"
        wallpaper_dir = self.wallpaper_cache_directory()
        file_path = wallpaper_dir / f"{key}.png"

        try:
            image_data = base64.b64decode(base64_string)
            with open(file_path, "wb") as f:
                f.write(image_data)
            self.device_wallpapers[key] = str(file_path)
            print(f"Wallpaper saved to: {file_path}")
            self.device_wallpapers_changed.emit()
        except Exception as e:
            print(f"Error saving wallpaper: {e}")

    @property
    def current_wallpaper_path(self) -> str | None:
        if not self.device:
            return None
        key = f"{self.device.name}-{self.device.ip_address}"
        return self.device_wallpapers.get(key)

    def set_plus_temporarily(self, value: bool):
        self.should_skip_save = True
        self.is_plus = value
        self.should_skip_save = False

    async def check_license_and_update_state(self, key: str = None):
        if key is None and self.license_details:
            key = self.license_details.key
        
        if key:
            details = await check_license_key_validity(key)
            if details:
                self.is_plus = True
                self.license_details = details
            else:
                self.is_plus = False
                self.license_details = None
        else:
            self.is_plus = False
            self.license_details = None
        
        if not self.should_skip_save:
            self.save_settings()
        self.is_plus_changed.emit(self.is_plus)
        self.license_details_changed.emit()

    def disconnect_device(self):
        from app.core.websocket_server import WebSocketServer
        WebSocketServer().send_disconnect_request()
        self.device = None
        self.notifications.clear()
        self.status = None
        self.device_changed.emit(self.device)
        self.notifications_changed.emit(self.notifications)
        self.status_changed.emit()

    def start_clipboard_monitoring(self):
        print("Starting clipboard monitoring.")
        self.last_clipboard_value = QGuiApplication.clipboard().text()
        self.clipboard_timer.start(1000)

    def stop_clipboard_monitoring(self):
        print("Stopping clipboard monitoring.")
        self.clipboard_timer.stop()

    def check_clipboard(self):
        current_clipboard = QGuiApplication.clipboard().text()
        if current_clipboard != self.last_clipboard_value:
            print(f"Clipboard changed: {current_clipboard}")
            self.last_clipboard_value = current_clipboard
            self.send_clipboard_to_android(current_clipboard)

    def send_clipboard_to_android(self, text: str):
        from app.core.websocket_server import WebSocketServer
        message = {"type": "clipboardUpdate", "data": {"text": text}}
        print(f"Preparing to send clipboard message: {message}")
        WebSocketServer().send_message(json.dumps(message))

    def update_clipboard_from_android(self, text: str):
        QGuiApplication.clipboard().setText(text)
        self.last_clipboard_value = text
