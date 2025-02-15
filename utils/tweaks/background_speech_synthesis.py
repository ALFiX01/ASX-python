import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class BackgroundSpeechSynthesisTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKLM\SOFTWARE\Policies\Microsoft\Speech"
        self.value_name = "AllowSpeechModelUpdate"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Фоновое обновление синтеза речи",
            description="Включает/отключает скрытое фоновое обновление моделей синтеза речи",
            category="Конфиденциальность"
        )
    def check_status(self) -> bool:
        """
        Проверяет, включено ли фоновое обновление синтеза речи.
        Обновление ВКЛЮЧЕНО, если AllowSpeechModelUpdate=1 (или ключ отсутствует).
        """
        try:
            value = self.reg.get_registry_value(self.registry_path, self.value_name)
            status = (value != 0)  # True, если обновление включено
            self.log_action("check_status", f"Background Speech Synthesis Update {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем, что обновление включено (поведение по умолчанию).
            self.log_action("check_status", "AllowSpeechModelUpdate key not found, assuming enabled", True)
            return True  # Обновление включено
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Background Speech Synthesis Update status: {e}")
            return True  # В случае ошибки считаем включенным


    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает фоновое обновление синтеза речи."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 1, winreg.REG_DWORD)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Background Speech Synthesis Update: {e}")
            return False

    def disable(self) -> bool:
        """Отключает фоновое обновление синтеза речи."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 0, winreg.REG_DWORD)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Background Speech Synthesis Update: {e}")
            return False
    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "background_speech_synthesis_log.txt")
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