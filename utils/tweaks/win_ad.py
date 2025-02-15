import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class WinAdTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Рекламный идентификатор Windows",
            description="Включает/отключает рекламный идентификатор и связанную с ним рекламу",
            category="Приватность"  # Твик приватности
        )

    def check_status(self) -> bool:
        """
        Проверяет, включен ли рекламный идентификатор.
        Идентификатор ВКЛЮЧЕН, если Enabled=1 в HKCU и AllowAdvertising=1 в HKLM.
        """
        try:
            enabled_hku = self.reg.get_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled")
            allow_advertising_hklm = self.reg.get_registry_value(r"HKLM\SOFTWARE\Microsoft\PolicyManager\current\device\Bluetooth", "AllowAdvertising")

            status = (enabled_hku == 1 and allow_advertising_hklm == 1)  # True, если включен
            self.log_action("check_status", f"Windows Advertising ID {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если какого-то из ключей нет, считаем, что отключено.
            self.log_action("check_status", "One or more registry keys not found, assuming disabled", True)
            return False  # Отключено
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Windows Advertising ID status: {e}")
            return False # В случае ошибки

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает рекламный идентификатор."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Windows Advertising ID: {e}")
            return False

    def disable(self) -> bool:
        """Отключает рекламный идентификатор."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Windows Advertising ID: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""
        value = 1 if enabled else 0
        self.reg.set_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", value, winreg.REG_DWORD)
        self.reg.set_registry_value(r"HKLM\SOFTWARE\Microsoft\PolicyManager\current\device\Bluetooth", "AllowAdvertising", value, winreg.REG_DWORD)


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "win_ad_log.txt")
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