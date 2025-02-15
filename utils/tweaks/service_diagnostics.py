import winreg
import subprocess
import os
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata

class DiagnosticsServicesTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.services = {
            "DiagTrack": r"HKLM\SYSTEM\CurrentControlSet\Services\DiagTrack",
            "dmwappushservice": r"HKLM\SYSTEM\CurrentControlSet\Services\dmwappushservice",
            "diagsvc": r"HKLM\SYSTEM\CurrentControlSet\Services\diagsvc",
            "DPS": r"HKLM\SYSTEM\CurrentControlSet\Services\DPS",
            "diagnosticshub.standardcollector.service": r"HKLM\SYSTEM\CurrentControlSet\Services\diagnosticshub.standardcollector.service",
            "WdiServiceHost": r"HKLM\SYSTEM\CurrentControlSet\Services\WdiServiceHost",
            "WdiSystemHost": r"HKLM\SYSTEM\CurrentControlSet\Services\WdiSystemHost",
        }
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Службы диагностики",
            description="Включает/отключает службы, связанные с диагностикой и сбором данных",
            category="Службы"
        )

    def check_status(self) -> bool:
        """Checks if all services are currently enabled."""
        for service_name, service_path in self.services.items():
            start_value = self.reg.get_registry_value(service_path, "Start")
            if start_value not in (2, 3):
                return False  # Return False if at least one service is disabled
        return True  # Return True only if all services are enabled

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if not current_status else "Enabled", result)
        return result

    def _set_service_startup(self, service_path, start_value):
        """Helper function to set the startup type for a service."""
        return self.reg.set_registry_value(service_path, "Start", start_value, winreg.REG_DWORD)

    def _start_service(self, service_name):
        """Helper function to start a service."""
        try:
            subprocess.run(["net", "start", service_name], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            self.log_action(f"start {service_name}", "Failed", False)
            print(f"Error starting {service_name}: {e}")
            return False

    def _stop_service(self, service_name):
        """Helper function to stop a service."""
        try:
            subprocess.run(["net", "stop", service_name], check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            self.log_action(f"stop {service_name}", "Failed", False)
            print(f"Error stopping {service_name}: {e}")
            return False

    def enable(self) -> bool:
        """Enables all diagnostics services."""
        overall_success = True
        for service_name, service_path in self.services.items():
            reg_result = self._set_service_startup(service_path, 2)
            start_result = self._start_service(service_name)
            overall_success = overall_success and reg_result and start_result
        self.log_action("enable", "Enabled", overall_success)
        return overall_success

    def disable(self) -> bool:
        """Disables all diagnostics services."""
        overall_success = True
        for service_name, service_path in self.services.items():
            reg_result = self._set_service_startup(service_path, 4)
            #В оригинальном коде в блоке else для WdiSystemHost стоит start 2 а не 4, допускаю что это опечатка
            #reg_result = self._set_service_startup(service_path, 2 if service_name == "WdiSystemHost" else 4)
            stop_result = self._stop_service(service_name)
            overall_success = overall_success and reg_result and stop_result
        self.log_action("disable", "Disabled", overall_success)
        return overall_success

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "diagnostics_services_log.txt")
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