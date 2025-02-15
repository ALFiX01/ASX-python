import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class UACTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Контроль учетных записей (UAC)",
            description="Включает/отключает контроль учетных записей пользователей (UAC)",
            category="Безопасность"  # Это твик безопасности
        )

    def check_status(self) -> bool:
        """
        Проверяет, включен ли UAC.
        UAC ВКЛЮЧЕН, если ConsentPromptBehaviorAdmin != 0.
        """
        try:
            value = self.reg.get_registry_value(self.registry_path, "ConsentPromptBehaviorAdmin")
            status = (value != 0)  # True, если UAC включен
            self.log_action("check_status", f"UAC {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем, что UAC включен (поведение по умолчанию).
            self.log_action("check_status", "ConsentPromptBehaviorAdmin key not found, assuming UAC enabled", True)
            return True  # UAC включен
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking UAC status: {e}")
            return True # В случае ошибки считаем, что включен

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает UAC."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling UAC: {e}")
            return False

    def disable(self) -> bool:
        """Отключает UAC."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling UAC: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""
        if enabled:
            values = {
                "ConsentPromptBehaviorAdmin": 5,
                "ConsentPromptBehaviorUser": 3,
                "EnableInstallerDetection": 1,
                "EnableLUA": 1,
                "EnableVirtualization": 1,
                "PromptOnSecureDesktop": 1,
                "ValidateAdminCodeSignatures": 0,
                "FilterAdministratorToken": 0,
            }
        else:
            values = {
                "ConsentPromptBehaviorAdmin": 0,
                "ConsentPromptBehaviorUser": 3,  # Оставляем 3, как в оригинальном batch
                "EnableInstallerDetection": 1, # Оставляем как в оригинале
                "EnableLUA": 1,                 # Оставляем как в оригинале
                "EnableVirtualization": 1,      # Оставляем как в оригинале
                "PromptOnSecureDesktop": 0,
                "ValidateAdminCodeSignatures": 0, # Оставляем как в оригинале
                "FilterAdministratorToken": 0, # Оставляем
            }

        for key, value in values.items():
            self.reg.set_registry_value(self.registry_path, key, value, winreg.REG_DWORD)



    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "uac_log.txt")
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