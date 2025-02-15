import os
import winreg
import subprocess
import datetime
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata


class HyperVServicesTweak(BaseTweak):
    def __init__(self):
        self.reg: RegistryHandler = RegistryHandler()
        self.services: dict[str, str] = {
            "vmickvpexchange": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\vmickvpexchange",
            "vmicshutdown": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\vmicshutdown",
            "vmicheartbeat": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\vmicheartbeat",
            "vmictimesync": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\vmictimesync",
            "vmicrdv": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\vmicrdv",
            "vmicguestinterface": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\vmicguestinterface",
            "vmicvmsession": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\vmicvmsession",
            "vmicvss": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\vmicvss",
        }
        self.value_name = "Start"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Службы Hyper-V",
            description="Включает/отключает службы Hyper-V.",
            category="Службы"
        )

    def check_status(self) -> bool:
        """
        Проверяет статус служб Hyper-V на основе значения 'Start' в реестре,
        игнорируя текущее состояние выполнения служб.
        """
        for service_name, registry_path in self.services.items():
            try:
                start_value = self.reg.get_registry_value(registry_path, self.value_name)
                if start_value in (2, 3):
                    return True  # Хотя бы одна служба включена (Automatic или Manual)
            except Exception as e:
                print(f"Ошибка при проверке статуса для {service_name}: {e}")
        return False  # Все службы отключены или возникли ошибки

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        success = True
        for service_name, registry_path in self.services.items():
            try:
                self.reg.set_registry_value(registry_path, self.value_name, 2, winreg.REG_DWORD)
                # Corrected:  Do NOT call net start
                self.log_action("enable", f"{service_name}: Enabled", True)

            except Exception as e:
                print(f"Error enabling {service_name}: {e}")
                self.log_action("enable", f"{service_name}: Failed to enable", False)
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
                self.log_action("disable", f"{service_name}: Failed to disable", False)
                success = False
        return success

    def setup_log_file(self):
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "services_hyperv_log.txt")
        return log_file

    def log_action(self, action, message, success):
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, Message: {message}, Success: {success}\n"
                f.write(log_message)
                print(log_message)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")