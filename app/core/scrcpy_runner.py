
import subprocess

class ScrcpyRunner:
    def __init__(self):
        self.scrcpy_path = 'scrcpy'

    def start_mirroring(self, device_id):
        try:
            subprocess.Popen([self.scrcpy_path, '-s', device_id])
        except FileNotFoundError:
            print(f"scrcpy not found at {self.scrcpy_path}")
        except Exception as e:
            print(f"An error occurred: {e}")
