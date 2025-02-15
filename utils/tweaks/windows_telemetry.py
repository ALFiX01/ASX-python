# utils/tweaks/windows_telemetry.py (с исправленной кодировкой)

import os
import winreg
import subprocess
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class WindowsTelemetryTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()
        # Определение кодировки OEM
        try:
            # chcp возвращает строку типа "Active code page: 866\n", поэтому берем только число
            self.oem_encoding = 'cp' + subprocess.check_output('chcp', shell=True, text=True).split(':')[-1].strip()
        except (subprocess.CalledProcessError, ValueError):
            # Если не удалось определить кодировку, используем cp866 как наиболее вероятную
            self.oem_encoding = 'cp866'
            print(f"Warning: Could not determine OEM codepage. Using default: {self.oem_encoding}")


    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Телеметрия Windows",
            description="Включает/отключает сбор телеметрии Windows и Office",
            category="Конфиденциальность"  # Твик конфиденциальности
        )

    def check_status(self) -> bool:
        """
        Проверяет, включена ли телеметрия (приблизительно).
        Телеметрия ВКЛЮЧЕНА, если Start в Diagtrack-Listener != 0 и DiagTrack != 4 и dmwappushservice != 4.
        Этот метод не идеален, т.к. не проверяет ВСЕ возможные настройки телеметрии.
        """
        try:
            diagtrack_listener_start = self.reg.get_registry_value(r"HKLM\SYSTEM\CurrentControlSet\Control\WMI\Autologger\Diagtrack-Listener", "Start")
            diagtrack_start = self.reg.get_registry_value(r"HKLM\SYSTEM\CurrentControlSet\Services\DiagTrack", "Start")
            dmwappushservice_start = self.reg.get_registry_value(r"HKLM\SYSTEM\CurrentControlSet\Services\dmwappushservice", "Start")

            # Если хоть что-то не отключено, то считаем, что телеметрия включена
            status = (diagtrack_listener_start != 0) or (diagtrack_start != 4) or (dmwappushservice_start != 4)
            self.log_action("check_status", f"Windows Telemetry {'Enabled' if status else 'Disabled'}", True)
            return status

        except FileNotFoundError:
            # Если какого-то ключа нет, считаем, что телеметрия включена.
            self.log_action("check_status", "One or more registry keys not found, assuming telemetry enabled", True)
            return True # Считаем что включена
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Windows Telemetry status: {e}")
            return True  # В случае ошибки считаем включенной

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает телеметрию Windows и Office."""
        try:
            self._set_registry_values(enabled=True)
            self._set_scheduled_tasks(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Windows Telemetry: {e}")
            return False

    def disable(self) -> bool:
        """Отключает телеметрию Windows и Office."""
        try:
            self._set_registry_values(enabled=False)
            self._set_scheduled_tasks(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Windows Telemetry: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""
        diagtrack_listener_start = 3 if enabled else 0
        save_zone_information = 3 if enabled else 1  # Этот параметр не был вынесен, т.к. меняется только он
        diagtrack_start = 3 if enabled else 4
        dmwappushservice_start = 3 if enabled else 4

        self.reg.set_registry_value(r"HKLM\SYSTEM\CurrentControlSet\Control\WMI\Autologger\Diagtrack-Listener", "Start", diagtrack_listener_start, winreg.REG_DWORD)
        self.reg.set_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Attachments", "SaveZoneInformation", save_zone_information, winreg.REG_DWORD)
        self.reg.set_registry_value(r"HKLM\SYSTEM\CurrentControlSet\Services\DiagTrack", "Start", diagtrack_start, winreg.REG_DWORD)
        self.reg.set_registry_value(r"HKLM\SYSTEM\CurrentControlSet\Services\dmwappushservice", "Start", dmwappushservice_start, winreg.REG_DWORD)


    def _set_scheduled_tasks(self, enabled: bool):
        """Включает/отключает запланированные задачи, связанные с телеметрией Office."""
        self.log_action("_set_scheduled_tasks", "Attempting", False)
        tasks = [
            r"Microsoft\Office\Office ClickToRun Service Monitor",
            r"Microsoft\Office\OfficeTelemetry\AgentFallBack2016",
            r"Microsoft\Office\OfficeTelemetry\OfficeTelemetryAgentLogOn2016",
            r"Microsoft\Office\OfficeTelemetryAgentFallBack",  # Добавлено для полноты
            r"Microsoft\Office\OfficeTelemetryAgentLogOn",      # Добавлено для полноты
            r"Microsoft\Office\Office 15 Subscription Heartbeat",
        ]
        action = "enable" if enabled else "disable"
        for task in tasks:
            try:
                subprocess.run(["schtasks", "/change", "/tn", task, f"/{action}"], check=True, capture_output=True, text=True, encoding=self.oem_encoding) # Используем self.oem_encoding
                self.log_action(f"_set_scheduled_tasks ({task})", f"{action.capitalize()}d", True)
            except subprocess.CalledProcessError as e:
                self.log_action(f"_set_scheduled_tasks ({task})", f"Failed to {action}", False)
                print(f"Error {action}ing scheduled task ({task}): {e}, stdout: {e.stdout}, stderr:{e.stderr}")
                # Не выходим, а продолжаем со следующей задачей
                # raise  #  Перевыбрасываем исключение -  теперь НЕ перевыбрасываем, чтобы продолжить выполнение


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "windows_telemetry_log.txt")
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