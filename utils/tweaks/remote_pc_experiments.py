import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler


class RemotePCExperimentsTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKLM\SOFTWARE\Microsoft\PolicyManager\current\device\System"
        self.value_name = "AllowExperimentation"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Удаленные эксперименты над ПК",
            description="Включает/отключает разрешение на проведение удаленных экспериментов над ПК",
            category="Конфиденциальность"
        )

    def check_status(self) -> bool:
        """
        Проверяет, разрешены ли удаленные эксперименты.
        Разрешены, если AllowExperimentation=1 (или ключа нет).
        """
        try:
            value = self.reg.get_registry_value(self.registry_path, self.value_name)
            status = (value != 0)  # True, если эксперименты разрешены
            self.log_action("check_status", f"Remote PC Experiments {'Allowed' if status else 'Disallowed'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем, что эксперименты разрешены (поведение по умолчанию).
            self.log_action("check_status", "AllowExperimentation key not found, assuming allowed", True)
            return True  # Эксперименты разрешены
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Remote PC Experiments status: {e}")
            return True # В случае ошибки


    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disallowed" if current_status else "Allowed", result)
        return result

    def enable(self) -> bool:
        """Разрешает удаленные эксперименты."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 1, winreg.REG_DWORD)
            self.log_action("enable", "Allowed", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to allow", False)
            print(f"Error allowing Remote PC Experiments: {e}")
            return False

    def disable(self) -> bool:
        """Запрещает удаленные эксперименты."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 0, winreg.REG_DWORD)
            self.log_action("disable", "Disallowed", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disallow", False)
            print(f"Error disallowing Remote PC Experiments: {e}")
            return False

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "remote_pc_experiments_log.txt")
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