# Код для utils/tweaks/app_start_notify.py (с исправленной логикой check_status)

import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class AppStartNotifyTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Предупреждения при запуске приложений",
            description="Включает/отключает предупреждения при запуске исполняемых файлов (.exe, .bat, и т.д.)",
            category="Оптимизация и настройки"  # Или "Безопасность"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включены ли предупреждения при запуске приложений.
        Предупреждения ВКЛЮЧЕНЫ, если DisableSecuritySettingsCheck=0 в HKLM (или ключ отсутствует).
        """
        try:
            value = self.reg.get_registry_value(
                r"HKLM\SOFTWARE\Microsoft\Internet Explorer\Security",
                "DisableSecuritySettingsCheck"
            )
            status = (value == 0)  # True, если предупреждения включены
            self.log_action("check_status", f"App Start Notifications {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключа нет, считаем, что предупреждения включены (поведение по умолчанию).
            self.log_action("check_status", "DisableSecuritySettingsCheck key not found, assuming notifications enabled", True)
            return True  # Предупреждения включены (по умолчанию)
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking App Start Notify status: {e}")
            return True  # В случае ошибки считаем, что включены

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает предупреждения при запуске приложений (возвращает стандартные настройки)."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling App Start Notify: {e}")
            return False

    def disable(self) -> bool:
        """Отключает предупреждения при запуске приложений."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling App Start Notify: {e}")
            return False


    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""

        disable_security_check_value = 0 if enabled else 1
        low_risk_file_types = ".exe;.bat;.cmd;.reg;.vbs;.msi;.msp;.com;.ps1;.ps2;.cpl"  # Используется только при отключении
        zone_3_1806_value = 0  # Всегда 0, согласно batch-скрипту

        # HKLM - DisableSecuritySettingsCheck
        self.reg.set_registry_value(
            r"HKLM\SOFTWARE\Microsoft\Internet Explorer\Security",
            "DisableSecuritySettingsCheck", disable_security_check_value, winreg.REG_DWORD
        )

        # HKCU - LowRiskFileTypes
        if not enabled:
            self.reg.set_registry_value(
                r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Associations",
                "LowRiskFileTypes", low_risk_file_types, winreg.REG_SZ
            )
        else:
             self.reg.delete_registry_value(
                r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Associations",
                "LowRiskFileTypes", ignore_not_found = True
            )

        # HKCU - Zones\3\1806
        self.reg.set_registry_value(
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3",
            "1806", zone_3_1806_value, winreg.REG_DWORD
        )


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app_start_notify_log.txt")
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