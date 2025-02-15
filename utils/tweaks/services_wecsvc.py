import os
import winreg
import subprocess
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata

class WecsvcServiceTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Wecsvc"
        self.value_name = "Start"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Служба Wecsvc",
            description="Включает/отключает службу сборщика событий Windows Wecsvc (Windows Event Collector).",
            category="Службы"
        )

    def check_status(self) -> bool:
        value = self.reg.get_registry_value(self.registry_path, self.value_name)
        # 2 - Automatic, 3 - Manual, 4 - Disabled.  Считаем включенной, если не 4.
        return value != 4

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 3, winreg.REG_DWORD)  # 3 - Manual
            # Попытка запустить службу
            result = subprocess.run(["net", "start", "Wecsvc"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.log_action("enable", "Enabled and started", True)
            elif result.returncode == 2:
                # Уже запущена
                self.log_action("enable", "Enabled (already running)", True)
            else:
                self.log_action("enable", f"Enabled, but failed to start: {result.stderr}", False)
                print(f"Failed to start Wecsvc: {result.stderr}")
            return True

        except Exception as e:
            print(f"Error enabling Wecsvc: {e}")
            self.log_action("enable", "Enabled", False)
            return False

    def disable(self) -> bool:
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 4, winreg.REG_DWORD)
            # Попытка остановить службу
            result = subprocess.run(["net", "stop", "Wecsvc"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.log_action("disable", "Disabled and stopped", True)
            elif result.returncode == 2:
                #Уже остановлена
                self.log_action("disable", "Disabled (already stopped)", True)
            else:
                self.log_action("disable", f"Disabled, but failed to stop: {result.stderr}", False)
                print(f"Failed to stop Wecsvc: {result.stderr}")
            return True

        except Exception as e:
            print(f"Error disabling Wecsvc: {e}")
            self.log_action("disable", "Disabled", False)
            return False

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "services_wecsvc_log.txt")
        return log_file

    def log_action(self, action, state, success):
        """Logs actions to the log file."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                print(log_message)  # Print to console too
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp formatted for logging."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")