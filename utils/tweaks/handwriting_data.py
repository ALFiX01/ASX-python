import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class HandwritingDataTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Данные рукописного ввода",
            description="Включает/отключает сбор и отправку данных рукописного ввода",
            category="Конфиденциальность"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включен ли сбор данных рукописного ввода.
        Сбор ВКЛЮЧЕН, если PreventHandwritingDataSharing=0, PreventHandwritingErrorReports=0 и Enabled=1 (HKCU).
        Если любого из ключей нет, считаем, что сбор отключен.
        """
        try:
            prevent_sharing = self.reg.get_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\TabletPC", "PreventHandwritingDataSharing")
            prevent_reports = self.reg.get_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\HandwritingErrorReports", "PreventHandwritingErrorReports")
            enabled_hku = self.reg.get_registry_value(r"HKCU\Software\Microsoft\Input\TIPC", "Enabled")

            # Сбор включен, если *все* условия истинны
            status = (prevent_sharing == 0 and prevent_reports == 0 and enabled_hku == 1)
            self.log_action("check_status", f"Handwriting Data Collection {'Enabled' if status else 'Disabled'}", True)
            return status # True, если сбор включен

        except FileNotFoundError:
            # Если какого-то ключа нет, считаем, что сбор отключен.
            self.log_action("check_status", "One or more registry keys not found, assuming disabled", True)
            return False # Отключен
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Handwriting Data Collection status: {e}")
            return False # В случае ошибки


    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает сбор данных рукописного ввода."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Handwriting Data Collection: {e}")
            return False

    def disable(self) -> bool:
        """Отключает сбор данных рукописного ввода."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Handwriting Data Collection: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""
        prevent_sharing_value = 0 if enabled else 1
        prevent_reports_value = 0 if enabled else 1
        enabled_hkcu_value = 1 if enabled else 0

        self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\TabletPC", "PreventHandwritingDataSharing", prevent_sharing_value, winreg.REG_DWORD)
        self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\HandwritingErrorReports", "PreventHandwritingErrorReports", prevent_reports_value, winreg.REG_DWORD)
        self.reg.set_registry_value(r"HKCU\Software\Microsoft\Input\TIPC", "Enabled", enabled_hkcu_value, winreg.REG_DWORD)


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "handwriting_data_log.txt")
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