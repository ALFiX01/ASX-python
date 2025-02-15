import os
import winreg
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata

class ShowFileExtensionsTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced"
        self.value_name = "HideFileExt"
        self.save_data_key = "HKCU\\Software\\ASX-Hub\\ParameterFunction"  # Замени на свой путь
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Показывать расширения файлов",
            description="Включает/отключает отображение расширений файлов в проводнике.",
            category="Кастомизация"  # Изменил категорию
        )

    def check_status(self) -> bool:
        value = self.reg.get_registry_value(self.registry_path, self.value_name)
        #  0 - показывать, 1 - скрывать.  True - показываем.
        return value == 0

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Hidden" if current_status else "Shown", result)  # Логируем "Shown" / "Hidden"
        return result
    def enable(self) -> bool:
        try:
            # Устанавливаем HideFileExt в 0 (показывать)
            self.reg.set_registry_value(self.registry_path, self.value_name, 0, winreg.REG_DWORD)
            #Сохраняем настройку в реестр
            self.reg.set_registry_value(self.save_data_key, "ShowFileExtensions", "1", winreg.REG_SZ)

            self.log_action("enable", "Shown", True)
            return True
        except Exception as e:
            print(f"Error enabling ShowFileExtensions: {e}")
            self.log_action("enable", "Shown", False)
            return False

    def disable(self) -> bool:
        try:
            # Устанавливаем HideFileExt в 1 (скрывать)
            self.reg.set_registry_value(self.registry_path, self.value_name, 1, winreg.REG_DWORD)
            #Удаляем настройку из реестра
            self.reg.delete_registry_value(self.save_data_key, "ShowFileExtensions")
            self.log_action("disable", "Hidden", True)
            return True
        except Exception as e:
            print(f"Error disabling ShowFileExtensions: {e}")
            self.log_action("disable", "Hidden", False)
            return False
    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "show_file_extensions_log.txt")
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