import os
import winreg
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata

class HomeExplorerTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.user_reg_path = "HKCU\\Software\\Classes\\CLSID\\{f874310e-b6b7-47dc-bc84-b9e6b38f5903}"
        self.system_reg_path = "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced\\NavPane\\ShowHome"
        self.value_name = "System.IsPinnedToNameSpaceTree"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Главная в проводнике",
            description="Включает/отключает отображение 'Главная' в панели навигации проводника.",
            category="Кастомизация"
        )
    def check_status(self) -> bool:
        value = self.reg.get_registry_value(self.user_reg_path, self.value_name)
        return value == 1

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        try:
            # Настройки пользователя
            self.reg.set_registry_value(self.user_reg_path, "", "CLSID_MSGraphHomeFolder", winreg.REG_SZ)  # Пустая строка для (Default)
            self.reg.set_registry_value(self.user_reg_path, self.value_name, 1, winreg.REG_DWORD)

            # Системные настройки
            self.reg.set_registry_value(self.system_reg_path, "CheckedValue", 1, winreg.REG_DWORD)
            self.reg.set_registry_value(self.system_reg_path, "DefaultValue", 1, winreg.REG_DWORD)
            self.reg.set_registry_value(self.system_reg_path, "HKeyRoot", 2147483649, winreg.REG_DWORD)
            self.reg.set_registry_value(self.system_reg_path, "Id", 13, winreg.REG_DWORD)
            self.reg.set_registry_value(self.system_reg_path, "RegPath", "Software\\Classes\\CLSID\\{f874310e-b6b7-47dc-bc84-b9e6b38f5903}", winreg.REG_SZ)
            self.reg.set_registry_value(self.system_reg_path, "Text", "Show Home", winreg.REG_SZ)
            self.reg.set_registry_value(self.system_reg_path, "Type", "checkbox", winreg.REG_SZ)
            self.reg.set_registry_value(self.system_reg_path, "UncheckedValue", 0, winreg.REG_DWORD)
            self.reg.set_registry_value(self.system_reg_path, "ValueName", "System.IsPinnedToNameSpaceTree", winreg.REG_SZ)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            print(f"Error enabling HomeExplorer: {e}")
            self.log_action("enable", "Enabled", False)
            return False
    def disable(self) -> bool:
        try:
            # Настройки пользователя
            self.reg.set_registry_value(self.user_reg_path, "", "CLSID_MSGraphHomeFolder", winreg.REG_SZ)  # Пустая строка для (Default)
            self.reg.set_registry_value(self.user_reg_path, self.value_name, 0, winreg.REG_DWORD)

            # Системные настройки
            self.reg.set_registry_value(self.system_reg_path, "CheckedValue", 1, winreg.REG_DWORD)
            self.reg.set_registry_value(self.system_reg_path, "DefaultValue", 0, winreg.REG_DWORD)  # DefaultValue = 0
            self.reg.set_registry_value(self.system_reg_path, "HKeyRoot", 2147483649, winreg.REG_DWORD)
            self.reg.set_registry_value(self.system_reg_path, "Id", 13, winreg.REG_DWORD)
            self.reg.set_registry_value(self.system_reg_path, "RegPath", "Software\\Classes\\CLSID\\{f874310e-b6b7-47dc-bc84-b9e6b38f5903}", winreg.REG_SZ)
            self.reg.set_registry_value(self.system_reg_path, "Text", "Show Home", winreg.REG_SZ)
            self.reg.set_registry_value(self.system_reg_path, "Type", "checkbox", winreg.REG_SZ)
            self.reg.set_registry_value(self.system_reg_path, "UncheckedValue", 0, winreg.REG_DWORD)
            self.reg.set_registry_value(self.system_reg_path, "ValueName", "System.IsPinnedToNameSpaceTree", winreg.REG_SZ)
            self.log_action("disable", "Disabled", True)
            return True

        except Exception as e:
            print(f"Error disabling HomeExplorer: {e}")
            self.log_action("disable", "Disabled", False)
            return False

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "home_explorer_log.txt")
        return log_file

    def log_action(self, action, state, success):
        """Logs actions to the log file."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                print(log_message)  # Print to console too
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp formatted for logging."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")