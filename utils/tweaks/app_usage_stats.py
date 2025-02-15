import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class AppUsageStatsTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Статистика использования приложений",
            description="Включает/отключает сбор статистики использования приложений",
            category="Конфиденциальность"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включен ли сбор статистики.
        Сбор ВКЛЮЧЕН, если AllowTelemetry=1, AITEnable=1 и Start_TrackProgs=1.
        Если хотя бы один из ключей отсутствует, считаем, что сбор отключен.
        """
        try:
            allow_telemetry_hklm_dc = self.reg.get_registry_value(r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry")
            ait_enable = self.reg.get_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\AppCompat", "AITEnable")
            allow_telemetry_hklm = self.reg.get_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry")
            start_track_progs = self.reg.get_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Start_TrackProgs")

            status = (allow_telemetry_hklm_dc == 1 and ait_enable == 1 and allow_telemetry_hklm == 1 and start_track_progs == 1)
            self.log_action("check_status", f"App Usage Stats Collection {'Enabled' if status else 'Disabled'}", True)
            return status  # True, если сбор включен

        except FileNotFoundError:
            # Если какого-то ключа нет, считаем, что сбор отключен
            self.log_action("check_status", "One or more registry keys not found, assuming disabled", True)
            return False
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking App Usage Stats Collection status: {e}")
            return False  # В случае ошибки считаем отключенным

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает сбор статистики использования приложений."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling App Usage Stats Collection: {e}")
            return False

    def disable(self) -> bool:
        """Отключает сбор статистики использования приложений."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling App Usage Stats Collection: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""
        value = 1 if enabled else 0

        self.reg.set_registry_value(r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry", value, winreg.REG_DWORD)
        self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\AppCompat", "AITEnable", value, winreg.REG_DWORD)
        self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", value, winreg.REG_DWORD)  # Дублирование!
        self.reg.set_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Start_TrackProgs", value, winreg.REG_DWORD)

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app_usage_stats_log.txt")
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