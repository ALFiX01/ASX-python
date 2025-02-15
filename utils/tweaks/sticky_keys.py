import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class StickyKeysTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.base_path = r"HKEY_CURRENT_USER\Control Panel\Accessibility"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Залипание клавиш",
            description="Включает/отключает залипание клавиш",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включено ли залипание клавиш.
        Залипание ВКЛЮЧЕНО, если значение Flags в StickyKeys равно "510".
        """
        try:
            value = self.reg.get_registry_value(f"{self.base_path}\\StickyKeys", "Flags")
            status = (value == "510")  # True если залипание включено
            self.log_action("check_status", f"Sticky Keys {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем, что залипание отключено (поведение по умолчанию).
            self.log_action("check_status", "StickyKeys Flags key not found, assuming sticky keys disabled", True)
            return False  # Залипание отключено
        except Exception as e:
            self.log_action("check_status", f"Error: {e}", False)
            print(f"Error checking Sticky Keys status: {e}")
            return False  # В случае ошибки считаем, что отключено

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает залипание клавиш и восстанавливает стандартные настройки."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Sticky Keys: {e}")
            return False

    def disable(self) -> bool:
        """Отключает залипание клавиш."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Sticky Keys: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра в зависимости от состояния (enabled)."""
        sticky_keys_flags = "510" if enabled else "506"
        sound_sentry_flags = "0"  # Всегда 0, согласно batch-скрипту
        keyboard_response_values = {
            "DelayBeforeAcceptance": "1000" if enabled else "0",
            "AutoRepeatRate": "500" if enabled else "0",
            "AutoRepeatDelay": "1000" if enabled else "0",
            "Flags": "126" if enabled else "122",
        }
        toggle_keys_flags = "62" if enabled else "58"

        self.reg.set_registry_value(f"{self.base_path}\\StickyKeys", "Flags", sticky_keys_flags, winreg.REG_SZ)
        self.reg.set_registry_value(f"{self.base_path}\\SoundSentry", "Flags", sound_sentry_flags, winreg.REG_SZ)

        for key, value in keyboard_response_values.items():
            self.reg.set_registry_value(f"{self.base_path}\\Keyboard Response", key, value, winreg.REG_SZ)

        self.reg.set_registry_value(f"{self.base_path}\\ToggleKeys", "Flags", toggle_keys_flags, winreg.REG_SZ)


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "sticky_keys_log.txt")
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