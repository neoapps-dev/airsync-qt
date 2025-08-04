import os
import asyncio
from app.core.app_state import AppState

class ADBConnector:

    @staticmethod
    def get_adb_path():
        return "adb"

    @staticmethod
    def get_scrcpy_path():
        return "scrcpy"

    @staticmethod
    async def _run_command_async(command: list[str]) -> str:
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            output = stdout.decode().strip() + stderr.decode().strip()
            return output
        except FileNotFoundError:
            return "Command not found."
        except Exception as e:
            return f"Error running command: {e}"

    @staticmethod
    async def connect_to_adb(ip: str, port: int):
        adb_path = ADBConnector.get_adb_path()
        if not os.path.exists(adb_path):
            AppState().adb_connection_result = "ADB binary not found."
            AppState().adb_connected = False
            return

        full_address = f"{ip}:{port}"
        await ADBConnector._run_command_async([adb_path, "kill-server"])
        output = await ADBConnector._run_command_async([adb_path, "connect", full_address])
        AppState().adb_connection_result = output
        if "connected to" in output.lower():
            AppState().adb_connected = True
        else:
            AppState().adb_connected = False

    @staticmethod
    async def disconnect_adb():
        adb_path = ADBConnector.get_adb_path()
        await ADBConnector._run_command_async([adb_path, "kill-server"])
        AppState().adb_connected = False

    @staticmethod
    async def start_scrcpy(ip: str, port: int, device_name: str, desktop: bool = False, package: str = None):
        scrcpy_path = ADBConnector.get_scrcpy_path()
        full_address = f"{ip}:{port}"
        device_name_formatted = device_name.replace("'", "").replace("s", "")
        args = [
            scrcpy_path,
            f"--window-title={device_name_formatted}",
            f"--tcpip={full_address}",
            "--video-bit-rate=3M",
            "--video-codec=h265",
            "--max-size=1200"
        ]

        if desktop:
            args.append("--new-display=2560x1440")

        if package:
            args.extend([
                "--new-display=500x800",
                f"--start-app={package}",
                "--no-vd-system-decorations"
            ])

        try:
            asyncio.create_subprocess_exec(*args)
            AppState().adb_connection_result = f"Started scrcpy on {full_address}"
        except FileNotFoundError:
            AppState().adb_connection_result = "scrcpy binary not found."
        except Exception as e:
            AppState().adb_connection_result = f"Failed to start scrcpy: {e}"