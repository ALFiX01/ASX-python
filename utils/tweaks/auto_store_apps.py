import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class AutoStoreAppsTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKLM\SOFTWARE\Policies\Microsoft\WindowsStore"
        self.value_name = "AutoDownload"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Автообновление приложений Магазина",
            description="Включает/отключает автоматическое обновление приложений из Microsoft Store",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включено ли автообновление приложений Магазина.
        Автообновление ВКЛЮЧЕНО, если AutoDownload отсутствует или не равно 2.
        """
        try:
            value = self.reg.get_registry_value(self.registry_path, self.value_name)
            status = (value != 2)  # True, если автообновление включено
            self.log_action("check_status", f"Auto Update Store Apps {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем, что автообновление включено (поведение по умолчанию).
            self.log_action("check_status", "AutoDownload key not found, assuming enabled", True)
            return True  # Автообновление включено
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Auto Update Store Apps status: {e}")
            return True # В случае ошибки

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает автоматическое обновление приложений Магазина."""
        try:
            # Удаляем ключ, чтобы включить автообновление (возврат к стандартному поведению)
            self.reg.delete_registry_value(self.registry_path, self.value_name, ignore_not_found=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Auto Update Store Apps: {e}")
            return False

    def disable(self) -> bool:
        """Отключает автоматическое обновление приложений Магазина."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 2, winreg.REG_DWORD)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Auto Update Store Apps: {e}")
            return False

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "auto_store_apps_log.txt")
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