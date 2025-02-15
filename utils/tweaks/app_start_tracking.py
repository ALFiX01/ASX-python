import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class AppStartTrackingTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        self.value_name = "Start_TrackProgs"
        self.log_file = self.setup_log_file()
        self.save_data_path = os.path.join(os.getenv('APPDATA'), "ASX-Hub", "SaveData", "ParameterFunction")
        self.param_value_name = "AppsTrack"

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Отслеживание запуска приложений",
            description="Включает/отключает отслеживание запуска приложений в меню \"Пуск\"",
            category="Конфиденциальность"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включено ли отслеживание запуска приложений.
        Отслеживание ВКЛЮЧЕНО, если Start_TrackProgs=1.
        Если ключа нет, считаем ОТКЛЮЧЕННЫМ.
        """
        try:
            value = self.reg.get_registry_value(self.registry_path, self.value_name)
            status = (value == 1)  # True - отслеживание включено
            self.log_action("check_status", f"App Start Tracking {'Enabled' if status else 'Disabled'}", True)
            return status  # True - если отслеживание включено
        except FileNotFoundError:
             # Если ключа нет, считаем, что отслеживание отключено
            self.log_action("check_status", "Start_TrackProgs key not found, assuming disabled", True)
            return False
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking App Start Tracking status: {e}")
            return False  # В случае ошибки считаем отключенным

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает отслеживание запуска приложений."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 1, winreg.REG_DWORD)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling App Start Tracking: {e}")
            return False

    def disable(self) -> bool:
        """Отключает отслеживание запуска приложений."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 0, winreg.REG_DWORD)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling App Start Tracking: {e}")
            return False
    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app_start_tracking_log.txt")
        return log_file

    def log_action(self, action, state, success):
        """Logs actions to the log file."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                print(log_message)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp formatted for logging."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")