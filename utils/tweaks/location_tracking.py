import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class LocationTrackingTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKLM\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Отслеживание местоположения",
            description="Включает/отключает отслеживание местоположения Windows",
            category="Конфиденциальность"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включено ли отслеживание местоположения.
        Отслеживание ВКЛЮЧЕНО, если DisableLocation=0, DisableLocationScripting=0 и DisableWindowsLocationProvider=0.
        Если любого из ключей нет, считаем отключенным
        """
        try:
            disable_location = self.reg.get_registry_value(self.registry_path, "DisableLocation")
            disable_scripting = self.reg.get_registry_value(self.registry_path, "DisableLocationScripting")
            disable_provider = self.reg.get_registry_value(self.registry_path, "DisableWindowsLocationProvider")

            status = (disable_location == 0 and disable_scripting == 0 and disable_provider == 0)
            self.log_action("check_status", f"Location Tracking {'Enabled' if status else 'Disabled'}", True)
            return status  # True, если отслеживание включено

        except FileNotFoundError:
            # Если какого-то ключа нет, считаем, что отслеживание отключено.
            self.log_action("check_status", "One or more registry keys not found, assuming disabled", True)
            return False # Отключено
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Location Tracking status: {e}")
            return False # В случае ошибки

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает отслеживание местоположения."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Location Tracking: {e}")
            return False

    def disable(self) -> bool:
        """Отключает отслеживание местоположения."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Location Tracking: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""
        value = 0 if enabled else 1
        self.reg.set_registry_value(self.registry_path, "DisableLocation", value, winreg.REG_DWORD)
        self.reg.set_registry_value(self.registry_path, "DisableLocationScripting", value, winreg.REG_DWORD)
        self.reg.set_registry_value(self.registry_path, "DisableWindowsLocationProvider", value, winreg.REG_DWORD)

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "location_tracking_log.txt")
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