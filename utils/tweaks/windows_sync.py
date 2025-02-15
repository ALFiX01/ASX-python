import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class WindowsSyncTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.base_path = r"HKCU\Software\Microsoft\Windows\CurrentVersion\SettingSync\Groups"
        self.log_file = self.setup_log_file()
        # Группы синхронизации
        self.sync_groups = [
            "Accessibility",
            "BrowserSettings",
            "Credentials",
            "Language",
            "Personalization",
            "Windows",
        ]


    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Синхронизация Windows",
            description="Включает/отключает синхронизацию настроек Windows",
            category="Конфиденциальность"  # Твик конфиденциальности
        )

    def check_status(self) -> bool:
        """
        Проверяет, включена ли синхронизация Windows.
        Синхронизация ВКЛЮЧЕНА, если Enabled=1 для *всех* групп.
        """
        try:
            all_enabled = True
            for group in self.sync_groups:
                value = self.reg.get_registry_value(f"{self.base_path}\\{group}", "Enabled")
                if value != 1:
                    all_enabled = False
                    break  # Если хоть одна группа отключена, выходим

            self.log_action("check_status", f"Windows Sync {'Enabled' if all_enabled else 'Disabled'}", True)
            return all_enabled
        except FileNotFoundError:
            # Если какого-то ключа нет, считаем, что синхронизация отключена.
            self.log_action("check_status", "One or more registry keys not found, assuming sync disabled", True)
            return False  # Синхронизация отключена
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Windows Sync status: {e}")
            return False # В случае ошибки


    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает синхронизацию Windows."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Windows Sync: {e}")
            return False

    def disable(self) -> bool:
        """Отключает синхронизацию Windows."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Windows Sync: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра для всех групп синхронизации."""
        value = 1 if enabled else 0
        for group in self.sync_groups:
            self.reg.set_registry_value(f"{self.base_path}\\{group}", "Enabled", value, winreg.REG_DWORD)

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "windows_sync_log.txt")
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