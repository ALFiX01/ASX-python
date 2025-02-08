import platform
import winreg
import os
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata


class PowerThrottlingTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling"
        self.value_name = "PowerThrottlingOff"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Power Throttling",
            description="Отключает/Включает Power Throttling",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        if platform.system() != "Windows":
            return False
        value = self.reg.get_registry_value(self.registry_path, self.value_name)
        # Power Throttling is DISABLED if the value is 1, ENABLED if 0 or None
        return value != 1

    def toggle(self) -> bool:
        current_status = self.check_status()
        # If currently enabled (check_status returns True), disable. If disabled, enable.
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if not current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        # Set PowerThrottlingOff to 0 to ENABLE Power Throttling
        result = self.reg.set_registry_value(
            self.registry_path,
            self.value_name,
            0,  # Corrected: 0 to ENABLE
            winreg.REG_DWORD
        )
        self.log_action("enable", "Enabled", result)
        return result

    def disable(self) -> bool:
        # Set PowerThrottlingOff to 1 to DISABLE Power Throttling
        result = self.reg.set_registry_value(
            self.registry_path,
            self.value_name,
            1,  # Corrected: 1 to DISABLE
            winreg.REG_DWORD
        )
        self.log_action("disable", "Disabled", result)
        return result

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "power_throttling_log.txt")
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