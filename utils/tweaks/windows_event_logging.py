import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class WindowsEventLoggingTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKLM\SYSTEM\CurrentControlSet\Services\diagnosticshub.standardcollector.service"
        self.value_name = "Start"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Журналирование событий Windows",
            description="Включает/отключает службу 'diagnosticshub.standardcollector.service'",
            category="Оптимизация и настройки"  # Или "Конфиденциальность", если считаете более подходящим
        )

    def check_status(self) -> bool:
        """
        Проверяет, включено ли журналирование событий Windows.
        Журналирование ВКЛЮЧЕНО, если Start != 4 (т.е. служба не отключена).
        """
        try:
            value = self.reg.get_registry_value(self.registry_path, self.value_name)
            status = (value != 4)  # True, если журналирование включено
            self.log_action("check_status", f"Windows Event Logging {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем службу отключенной.
            self.log_action("check_status", "diagnosticshub.standardcollector.service Start key not found, assuming disabled", True)
            return False  # Отключено
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Windows Event Logging status: {e}")
            return False # В случае ошибки

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает журналирование событий Windows."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 3, winreg.REG_DWORD)  # 3 - Manual
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Windows Event Logging: {e}")
            return False

    def disable(self) -> bool:
        """Отключает журналирование событий Windows."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 4, winreg.REG_DWORD)  # 4 - Disabled
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Windows Event Logging: {e}")
            return False
    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "windows_event_logging_log.txt")
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