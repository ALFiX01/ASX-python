import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class MouseAccelerationTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKCU\Control Panel\Mouse"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Ускорение мыши",
            description="Включает/отключает повышенную точность установки указателя мыши (ускорение)",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включено ли ускорение мыши.
        Ускорение ВКЛЮЧЕНО, если MouseSpeed НЕ равно 0.
        """
        try:
            mouse_speed = self.reg.get_registry_value(self.registry_path, "MouseSpeed")
            status = (mouse_speed != "0")  # True, если ускорение включено
            self.log_action("check_status", f"Mouse Acceleration {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем, что ускорение включено (поведение по умолчанию).
            self.log_action("check_status", "MouseSpeed key not found, assuming acceleration enabled", True)
            return True
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking mouse acceleration status: {e}")
            return True  # В случае ошибки считаем, что включено

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает ускорение мыши (возвращает стандартные настройки)."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling mouse acceleration: {e}")
            return False

    def disable(self) -> bool:
        """Отключает ускорение мыши."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling mouse acceleration: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""
        mouse_speed = "1" if enabled else "0"
        mouse_threshold1 = "6" if enabled else "0"
        mouse_threshold2 = "10" if enabled else "0"

        self.reg.set_registry_value(self.registry_path, "MouseSpeed", mouse_speed, winreg.REG_SZ)
        self.reg.set_registry_value(self.registry_path, "MouseThreshold1", mouse_threshold1, winreg.REG_SZ)
        self.reg.set_registry_value(self.registry_path, "MouseThreshold2", mouse_threshold2, winreg.REG_SZ)

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "mouse_acceleration_log.txt")
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