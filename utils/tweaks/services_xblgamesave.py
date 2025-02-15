import os
import winreg
import subprocess
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata

class XblGameSaveServicesTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.services = {
            "XblGameSave": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\XblGameSave",
            "XboxNetApiSvc": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\XboxNetApiSvc",
            "XboxGipSvc": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\XboxGipSvc",
            "XblAuthManager": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\XblAuthManager",
        }
        self.value_name = "Start"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Службы Xbox",
            description="Включает/отключает службы Xbox (XblGameSave, XboxNetApiSvc, XboxGipSvc, XblAuthManager).",
            category="Службы"
        )

    def check_status(self) -> bool:
        for service_name, registry_path in self.services.items():
            value = self.reg.get_registry_value(registry_path, self.value_name)
            if value != 4:
                return True
        return False

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        success = True
        for service_name, registry_path in self.services.items():
            try:
                self.reg.set_registry_value(registry_path, self.value_name, 2, winreg.REG_DWORD)  # 2 - Automatic
                result = subprocess.run(["net", "start", service_name], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.log_action("enable", f"{service_name}: Enabled and started", True)
                elif result.returncode == 2:
                    self.log_action("enable", f"{service_name}: Enabled (already running)", True)
                else:
                    self.log_action("enable", f"{service_name}: Enabled, but failed to start: {result.stderr}", False)
                    print(f"Failed to start {service_name}: {result.stderr}")
                    success = False
            except Exception as e:
                print(f"Error enabling {service_name}: {e}")
                self.log_action("enable", f"{service_name}: Enabled", False)
                success = False
        return success

    def disable(self) -> bool:
        success = True
        for service_name, registry_path in self.services.items():
            try:
                self.reg.set_registry_value(registry_path, self.value_name, 4, winreg.REG_DWORD)
                result = subprocess.run(["net", "stop", service_name], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.log_action("disable", f"{service_name}: Disabled and stopped", True)
                elif result.returncode == 2:
                    self.log_action("disable", f"{service_name}: Disabled (already stopped)", True)
                else:
                    self.log_action("disable", f"{service_name}: Disabled, but failed to stop: {result.stderr}", False)
                    print(f"Failed to stop {service_name}: {result.stderr}")
                    success = False
            except Exception as e:
                print(f"Error disabling {service_name}: {e}")
                self.log_action("disable", f"{service_name}: Disabled", False)
                success = False
        return success

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "services_xblgamesave_log.txt")
        return log_file

    def log_action(self, action, message, success):
        """Logs actions to the log file."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, Message: {message}, Success: {success}\n"
                f.write(log_message)
                print(log_message)  # Print to console too
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp formatted for logging."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")