import asyncio
import json
import websockets
from PySide6.QtCore import QObject, Signal
from app.core.app_state import AppState
from app.model.device import Device
from app.model.notification import Notification
from app.model.device_status import DeviceStatus, Battery, Music
import base64
import os
import io
from PIL import Image
from app.constants import Defaults
import logging
from pathlib import Path
log_dir = Path.home() / ".airsync" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "websocket.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger(__name__)

def app_cache_directory(sub_folder):
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "airsync-qt", sub_folder)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def app_icons_directory():
    return app_cache_directory("AppIcons")


class WebSocketServer(QObject):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            super().__init__()
            self._initialized = True
            self.server = None
            self.active_sessions = set()
            self.loop = None

    message_received = Signal(dict)

    async def start(self, port=Defaults.server_port):
        self.loop = asyncio.get_running_loop()
        try:
            self.server = await websockets.serve(self.handler, "0.0.0.0", port, max_size=5 * 1024 * 1024)
            AppState().websocket_status = "started"
            print(f"WebSocket server started at ws://0.0.0.0:{port}")
        except Exception as e:
            AppState().websocket_status = f"failed: {e}"
            print(f"Failed to start WebSocket server: {e}")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
            AppState().websocket_status = "stopped"

    async def handler(self, websocket):
        self.active_sessions.add(websocket)
        try:
            async for message in websocket:
                print(f"WebSocket received: {message}")
                try:
                    data = json.loads(message)
                    self.handle_message(data)
                except json.JSONDecodeError:
                    print(f"WebSocket JSON decode failed: {message}")
        finally:
            self.active_sessions.remove(websocket)
            if not self.active_sessions:
                AppState().disconnect_device()

    def handle_message(self, message):
        message_type = message.get("type")
        data = message.get("data")

        if message_type == "device": 
            device_data = {
                "name": data.get("name"),
                "ip_address": data.get("ipAddress"),
                "port": data.get("port"),
            }
            device = Device(**device_data)
            AppState().device = device
            AppState().device_changed.emit(device)

            wallpaper = data.get("wallpaper")
            if wallpaper:
                AppState().save_wallpaper_from_base64(wallpaper)
        elif message_type == "notification":
            notification_data = {
                "title": data.get("title"),
                "body": data.get("body"),
                "app": data.get("app"),
                "nid": data.get("id"),
                "package": data.get("package")
            }
            notification = Notification(**notification_data)
            AppState().add_notification(notification)
            coro = AppState().post_native_notification(
                id=notification.nid,
                app_name=notification.app,
                title=notification.title,
                body=notification.body,
                package=notification.package
            )
            if self.loop:
                asyncio.run_coroutine_threadsafe(coro, self.loop)
        elif message_type == "status":
            battery_data = data.get("battery", {})
            music_data = data.get("music", {})

            battery = Battery(
                level=battery_data.get("level"),
                is_charging=battery_data.get("isCharging")
            )
            music = Music(
                title=music_data.get("title"),
                artist=music_data.get("artist"),
                is_playing=music_data.get("isPlaying"),
                volume=music_data.get("volume"),
                is_muted=music_data.get("isMuted", False)
            )
            status = DeviceStatus(
                battery=battery,
                is_paired=data.get("isPaired"),
                music=music
            )
            AppState().status = status
            AppState().status_changed.emit()
        elif message_type == "appIcons":
            logger.debug(f"Received appIcons message: {data}")
            for package, base64_icon in data.items():
                cleaned_base64 = base64_icon
                if "base64," in cleaned_base64:
                    cleaned_base64 = cleaned_base64.split("base64,", 1)[1]
                valid_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
                original_cleaned_base64 = cleaned_base64
                cleaned_base64 = "".join(c for c in cleaned_base64 if c in valid_chars)
                if original_cleaned_base64 != cleaned_base64:
                    logger.debug(f"Removed invalid characters from base64 string. Original length: {len(original_cleaned_base64)}, New length: {len(cleaned_base64)}")
                    missing_padding = len(cleaned_base64) % 4
                    if missing_padding != 0:
                        cleaned_base64 += '=' * (4 - missing_padding)

                logger.debug(f"Cleaned base64 (after stripping and validation): {cleaned_base64[:50]}... (len: {len(cleaned_base64)})")
                logger.debug(f"Attempting to decode base64 string (first 100 chars): {cleaned_base64[:100]}... (len: {len(cleaned_base64)})")
                try:
                    icon_data = base64.b64decode(cleaned_base64)
                    image = Image.open(io.BytesIO(icon_data))
                    file_path = os.path.join(app_icons_directory(), f"{package}.png")
                    image.save(file_path, "PNG")
                    AppState().app_icons[package] = file_path
                except (base64.binascii.Error, Exception) as e:
                    logger.error(f"Error decoding app icon for {package}: {e}")
                    logger.error(f"Problematic string (first 100 chars): {cleaned_base64[:100]}...")
                    logger.error(f"Length of problematic string: {len(cleaned_base64)}")
            AppState().app_icons_changed.emit()
        elif message_type == "clipboardUpdate":
            AppState().update_clipboard_from_android(data.get("text"))
        elif message_type == "wallpaperImage":
            base64_string = data.get("wallpaper")
            print(f"Received wallpaper image data: {base64_string[:50]}...")
            if base64_string:
                AppState().save_wallpaper_from_base64(base64_string)

    def send_message(self, message):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self._send_message_async(message), self.loop)
        else:
            print("WebSocket event loop not available. Cannot send message.")

    async def _send_message_async(self, message):
        print(f"WebSocket sending: {message}")
        if self.active_sessions:
            await asyncio.gather(
                *[session.send(message) for session in self.active_sessions]
            )
        else:
            print("No active WebSocket sessions to send message to.")

    def send_disconnect_request(self):
        message = {"type": "disconnectRequest", "data": {}}
        self.send_message(json.dumps(message))

    def dismiss_notification(self, nid):
        message = {"type": "dismissNotification", "data": {"id": nid}}
        self.send_message(json.dumps(message))

    def send_media_action(self, action):
        message = {"type": "mediaControl", "data": {"action": action}}
        self.send_message(json.dumps(message))

    def send_volume_action(self, action, volume=None):
        data = {"action": action}
        if volume is not None:
            data["volume"] = volume
        message = {"type": "volumeControl", "data": data}
        self.send_message(json.dumps(message))

    def send_clipboard_update(self, message):
        self.send_message(message)
