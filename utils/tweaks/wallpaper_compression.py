import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class WallpaperCompressionTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKCU\Control Panel\Desktop"
        self.value_name = "JPEGImportQuality"
        self.log_file = self.setup_log_file()
        self.default_setting_value = 85  # Значение по умолчанию

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Сжатие обоев",
            description="Включает/отключает сжатие JPEG для обоев рабочего стола",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включено ли сжатие обоев.
        Сжатие ВКЛЮЧЕНО, если значение JPEGImportQuality НЕ равно 256 (или ключ отсутствует).
        """
        try:
            value = self.reg.get_registry_value(self.registry_path, self.value_name)
            status = (value != 256)  # True, если сжатие включено
            self.log_action("check_status", f"Compression {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем, что сжатие включено (используется значение по умолчанию).
            self.log_action("check_status", "JPEGImportQuality key not found, assuming compression enabled", True)
            return True
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking wallpaper compression status: {e}")
            return True  # В случае ошибки считаем, что сжатие включено

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()  # Если включено - выключаем, и наоборот.
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает сжатие обоев (устанавливает значение из переменной окружения или значение по умолчанию)."""
        try:
            df_setting_value = int(os.getenv("DFSettingValue", str(self.default_setting_value)))
            self.reg.set_registry_value(self.registry_path, self.value_name, df_setting_value, winreg.REG_DWORD)
            self.log_action("enable", f"Enabled (set to {df_setting_value})", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling wallpaper compression: {e}")
            return False

    def disable(self) -> bool:
        """Отключает сжатие обоев (устанавливает значение 256)."""
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 256, winreg.REG_DWORD)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling wallpaper compression: {e}")
            return False

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "wallpaper_compression_log.txt")
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