import sys
import asyncio
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer

from app.core.app_state import AppState
from app.core.websocket_server import WebSocketServer
from app.ui.views.home_view import HomeView

class AirSyncApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.app_state = AppState()
        self.websocket_server = WebSocketServer()
        self.main_window = QMainWindow()
        self.home_view = HomeView()
        self.main_window.setCentralWidget(self.home_view)
        self.main_window.setWindowTitle("AirSync")
        self.main_window.resize(1000, 600)
        self.main_window.show()
        self.loop = asyncio.get_event_loop()
        self.timer = QTimer()
        self.timer.timeout.connect(self._run_asyncio_tasks)
        self.timer.start(10)
        asyncio.ensure_future(self.websocket_server.start(port=self.app_state.port))

    def _run_asyncio_tasks(self):
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()

    def restart_websocket_server(self):
        asyncio.ensure_future(self.websocket_server.stop())
        asyncio.ensure_future(self.websocket_server.start(port=self.app_state.port))

    def closeEvent(self, event):
        asyncio.ensure_future(self.websocket_server.stop())
        self.loop.call_soon_threadsafe(self.loop.stop)
        super().closeEvent(event)

if __name__ == "__main__":
    app = AirSyncApp(sys.argv)
    sys.exit(app.exec())