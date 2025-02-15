import os
import subprocess
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler


class WindowsDefenderTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Защитник Windows (Windows Defender)",
            description="Включает/отключает Защитник Windows (Windows Defender)",
            category="Безопасность"  # Изменено на "Безопасность"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включен ли Защитник Windows.  Использует PowerShell для получения
        более точного статуса, чем просто проверка реестра.
        """
        try:
            result = subprocess.run(
                ["powershell", "-command", "Get-MpComputerStatus | Select-Object -ExpandProperty AMServiceEnabled"],
                capture_output=True, text=True, check=True
            )
            # result.stdout будет содержать "True" или "False" (как строку)
            status = result.stdout.strip().lower() == "true"
            self.log_action("check_status", f"WindowsDefender: {status}", True)  # Логируем результат проверки
            return status
        except subprocess.CalledProcessError as e:
            self.log_action("check_status", "WindowsDefender Error checking status", False)
            print(f"Error checking Windows Defender status: {e}")
            return False  # В случае ошибки считаем, что отключен


    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if not current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает Защитник Windows."""
        try:
            # Удаляем ключ автозапуска (если есть)
            self.reg.delete_registry_value(r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run", "Windows Defender", ignore_not_found=True)

            # Настройки реестра для включения
            self._set_defender_reg_values(enable=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Enabled", False)
            print(f"An unexpected error occurred: {e}")
            return False

    def disable(self) -> bool:
        """Отключает Защитник Windows."""
        try:
            # Добавляем ключ автозапуска
            self.reg.set_registry_value(
                r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run",
                "Windows Defender",
                r'"C:\Program Files\Windows Defender\MSASCui.exe" -hide -runkey',
                winreg.REG_SZ
            )

            # Настройки реестра для отключения
            self._set_defender_reg_values(enable=False)
            self.log_action("disable", "Disabled", True)
            return True

        except Exception as e:
            self.log_action("disable", "Disabled", False)
            print(f"An unexpected error occurred: {e}")
            return False

    def _set_defender_reg_values(self, enable: bool):
        """Вспомогательная функция для установки значений реестра."""
        value = 0 if enable else 1
        delete_value = 0 if not enable else 1

        # Общие настройки
        self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware", value, winreg.REG_DWORD)
        self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection", "DisableRealtimeMonitoring", value, winreg.REG_DWORD)


        if not enable:
            self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection", "DisableBehaviorMonitoring", 1, winreg.REG_DWORD)
            self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection", "DisableOnAccessProtection", 1, winreg.REG_DWORD)
            self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection", "DisableScanOnRealtimeEnable", 1, winreg.REG_DWORD)
            #Удаление ключей
            self.reg.delete_registry_key(r"HKCR\*\shellex\ContextMenuHandlers\EPP", ignore_not_found=True)
            self.reg.delete_registry_key(r"HKCR\Directory\shellex\ContextMenuHandlers\EPP", ignore_not_found=True)
            self.reg.delete_registry_key(r"HKCR\Drive\shellex\ContextMenuHandlers\EPP", ignore_not_found=True)


        # UX Configuration
        self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\UX Configuration", "Notification_Suppress", value, winreg.REG_DWORD)

        # Сервисы
        services = {
            "WdBoot": 0 if enable else 4,
            "WdFilter": 0 if enable else 4,
            "WdNisDrv": 3 if enable else 4,
            "WdNisSvc": 3 if enable else 4,
            "WinDefend": 2 if enable else 4,
            "SecurityHealthService": 2 if enable else 4,
            "wscsvc": 2 if enable else 4,
        }
        for service_name, start_value in services.items():
            self.reg.set_registry_value(r"HKLM\SYSTEM\CurrentControlSet\Services\\" + service_name, "Start", start_value, winreg.REG_DWORD)


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "windows_defender_log.txt")
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