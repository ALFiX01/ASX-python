import winreg
import subprocess
import os
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata

class SysMainServiceTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.service_path = r"HKLM\SYSTEM\CurrentControlSet\Services\SysMain"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Служба SysMain",
            description="Включает/отключает службу SysMain",
            category="Службы"
        )

    def check_status(self) -> bool:
        """Checks if the service is currently enabled."""
        start_value = self.reg.get_registry_value(self.service_path, "Start")
        # Service is considered ENABLED if Start value is 2 (Automatic) OR 3 (Manual).
        return start_value in (2, 3)

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if not current_status else "Enabled", result)
        return result

    def _set_service_startup(self, start_value):
        """Helper function to set the startup type for the service."""
        return self.reg.set_registry_value(self.service_path, "Start", start_value, winreg.REG_DWORD)

    def _start_service(self):
        """Helper function to start the service."""
        try:
            subprocess.run(["net", "start", "SysMain"], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            self.log_action("start SysMain", "Failed", False)
            print(f"Error starting SysMain: {e}")
            return False

    def _stop_service(self):
        """Helper function to stop the service."""
        try:
            subprocess.run(["net", "stop", "SysMain"], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            self.log_action("stop SysMain", "Failed", False)
            print(f"Error stopping SysMain: {e}")
            return False

    def enable(self) -> bool:
        """Enables the SysMain service."""
        reg_result = self._set_service_startup(2)
        start_result = self._start_service()
        overall_success = reg_result and start_result
        self.log_action("enable", "Enabled", overall_success)
        return overall_success

    def disable(self) -> bool:
        """Disables the SysMain service."""
        reg_result = self._set_service_startup(4)
        stop_result = self._stop_service()
        overall_success = reg_result and stop_result
        self.log_action("disable", "Disabled", overall_success)
        return overall_success
    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "sysmain_service_log.txt") #Не меняем имя лог файла
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