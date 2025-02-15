import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class SecurityCenterNotificationsTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Уведомления Центра безопасности",
            description="Включает/отключает уведомления Центра безопасности Windows",
            category="Безопасность"  # Корректная категория
        )

    def check_status(self) -> bool:
        """
        Проверяет, отключены ли уведомления Центра безопасности.
        Уведомления ОТКЛЮЧЕНЫ, если Enabled=0 в HKCU.
        """
        try:
            value = self.reg.get_registry_value(
                r"HKCU\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings\Windows.SystemToast.SecurityAndMaintenance",
                "Enabled"
            )
            status = (value == 0)  # True, если уведомления отключены
            self.log_action("check_status", f"Security Center Notifications {'Disabled' if status else 'Enabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем, что уведомления включены (поведение по умолчанию).
            self.log_action("check_status", "Enabled key not found in HKCU, assuming notifications enabled", True)
            return False # Уведомления включены
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Security Center Notifications status: {e}")
            return False  # В случае ошибки считаем, что включены.


    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.enable() if current_status else self.disable()
        self.log_action("toggle", "Enabled" if current_status else "Disabled", result)
        return result


    def enable(self) -> bool:
        """Включает уведомления Центра безопасности (возвращает стандартные настройки)."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Security Center Notifications: {e}")
            return False

    def disable(self) -> bool:
        """Отключает уведомления Центра безопасности."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Security Center Notifications: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""

        # Значения для включения/отключения уведомлений
        enabled_value = 0 if not enabled else None  # Если enabled=False, ставим 0.  Если enabled=True, то None (удаляем ключ).
        disable_notifications_value = 1 if not enabled else 0

        # HKCU
        if enabled_value is not None:
            self.reg.set_registry_value(
                r"HKCU\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings\Windows.SystemToast.SecurityAndMaintenance",
                "Enabled", enabled_value, winreg.REG_DWORD
            )
        else:
            self.reg.delete_registry_value(  # <---  Вот здесь используем ignore_not_found=True
                r"HKCU\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings\Windows.SystemToast.SecurityAndMaintenance",
                "Enabled", ignore_not_found=True
            )

        # HKLM - Notifications\Settings
        if enabled_value is not None:
            self.reg.set_registry_value(
                r"HKLM\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings\Windows.SystemToast.SecurityAndMaintenance",
                "Enabled", enabled_value, winreg.REG_DWORD
            )
        else:
            self.reg.delete_registry_value(  # <---  И здесь тоже
                r"HKLM\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings\Windows.SystemToast.SecurityAndMaintenance",
                "Enabled", ignore_not_found=True
            )

        # HKLM - Windows Defender Security Center\Notifications
        self.reg.set_registry_value(
            r"HKLM\SOFTWARE\Microsoft\Windows Defender Security Center\Notifications",
            "DisableNotifications", disable_notifications_value, winreg.REG_DWORD
        )

        # HKLM - Policies
        self.reg.set_registry_value(
            r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender Security Center\Notifications",
            "DisableNotifications", disable_notifications_value, winreg.REG_DWORD
        )


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "security_center_notifications_log.txt")
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