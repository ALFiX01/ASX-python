import os
import winreg
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
import subprocess

class TaskbarDateTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = "HKCU\\Control Panel\\International"
        self.value_name = "sShortDate"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Дата на панели задач",
            description="Включает/отключает отображение дня недели на панели задач.",
            category="Кастомизация"
        )

    def check_status(self) -> bool:
        value = self.reg.get_registry_value(self.registry_path, self.value_name)
        # Проверяем, содержит ли строка "ddd" (день недели)
        return "ddd" in str(value)

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, "ddd-dd.MM.yyyy", winreg.REG_SZ)
            self.log_action("enable", "Enabled", True)
            self.restart_explorer()
            return True
        except Exception as e:
            print(f"Error enabling TaskbarDate: {e}")
            self.log_action("enable", "Enabled", False)
            return False

    def disable(self) -> bool:
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, "dd.MM.yyyy", winreg.REG_SZ)
            self.log_action("disable", "Disabled", True)
            self.restart_explorer()
            return True
        except Exception as e:
            print(f"Error disabling TaskbarDate: {e}")
            self.log_action("disable", "Disabled", False)
            return False

    def restart_explorer(self):
        """Перезапускает explorer.exe."""
        try:
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=True, shell=True)
            subprocess.run(["explorer.exe"], check=True, shell=True)
            self.log_action("restart_explorer", "Explorer restarted", True)
        except Exception as e:
            self.log_action("restart_explorer", f"Error restarting explorer: {e}", False)
            print(f"Error restarting explorer: {e}")
    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "taskbar_date_log.txt")
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