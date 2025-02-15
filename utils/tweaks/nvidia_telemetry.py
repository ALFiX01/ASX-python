import os
import winreg
import subprocess
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class NvidiaTelemetryTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKLM\SYSTEM\CurrentControlSet\Services\NvTelemetryContainer"
        self.value_name = "Start"
        self.log_file = self.setup_log_file()
        self.service_name = "NvTelemetryContainer"
        # Задачи, связанные с телеметрией NVIDIA (GUID может отличаться в разных системах!)
        self.tasks = [
            "NvTmRepOnLogon_{B2FE1952-0186-46C3-BAEC-A80AA35AC5B8}",  # Пример GUID
            "NvTmRep_{B2FE1952-0186-46C3-BAEC-A80AA35AC5B8}",
            "NvTmMon_{B2FE1952-0186-46C3-BAEC-A80AA35AC5B8}",
        ]


    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Телеметрия NVIDIA",
            description="Включает/отключает службу и задачи телеметрии NVIDIA",
            category="Оптимизация и настройки"
        )
    def check_status(self) -> bool:
        """
        Проверяет, включена ли телеметрия NVIDIA (приблизительно).
        Считаем, что телеметрия ВКЛЮЧЕНА, если служба NvTelemetryContainer НЕ отключена (Start != 4)
        """
        try:
            start_value = self.reg.get_registry_value(self.registry_path, self.value_name)
            status = (start_value != 4)  # True, если телеметрия включена
            self.log_action("check_status", f"NVIDIA Telemetry {'Enabled' if status else 'Disabled'}", True)
            return status  # True - телеметрия ВКЛЮЧЕНА
        except FileNotFoundError:
            # Если ключа нет, считаем службу отключенной.
            self.log_action("check_status", "NvTelemetryContainer Start key not found, assuming disabled", True)
            return False
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking NVIDIA Telemetry status: {e}")
            return False  # В случае ошибки считаем отключенной

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает телеметрию NVIDIA."""
        try:
            # Устанавливаем значение Start в реестре (2 - Automatic, 3 - Manual)
            self.reg.set_registry_value(self.registry_path, self.value_name, 3, winreg.REG_DWORD)

            # Включаем и запускаем службу
            self._control_service(enable=True)

            # Включаем запланированные задачи
            self._control_tasks(enable=True)

            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling NVIDIA Telemetry: {e}")
            return False

    def disable(self) -> bool:
        """Отключает телеметрию NVIDIA."""
        try:
            # Устанавливаем значение Start в реестре (4 - Disabled)
            self.reg.set_registry_value(self.registry_path, self.value_name, 4, winreg.REG_DWORD)

            # Останавливаем и отключаем службу
            self._control_service(enable=False)


            # Отключаем запланированные задачи
            self._control_tasks(enable=False)

            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling NVIDIA Telemetry: {e}")
            return False

    def _control_service(self, enable: bool):
        """Управляет службой NvTelemetryContainer (включение/отключение, запуск/остановка)."""
        action = "enable" if enable else "disable"
        start_type = "auto" if enable else "disabled"  # Тип запуска службы

        try:
            # Изменяем тип запуска службы
            subprocess.run(["sc", "config", self.service_name, "start=", start_type], check=True, capture_output=True, text=True)

            # Запускаем или останавливаем службу
            service_command = "start" if enable else "stop"
            try:
                subprocess.run(["net", service_command, self.service_name], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                if enable and "The service has not been started" not in e.stderr:
                    # Если включаем и служба еще не запущена, это нормально.
                    raise
                elif not enable and ("The service has already been started" not in e.stderr and "The service is not started" not in e.stderr) :
                    # Если отключаем, и служба уже остановлена - тоже нормально.
                    raise

            self.log_action(f"_control_service ({self.service_name})", f"{action.capitalize()}d", True)

        except subprocess.CalledProcessError as e:
            self.log_action(f"_control_service ({self.service_name})", f"Failed to {action}", False)
            print(f"Error controlling service ({self.service_name}): {e}, stdout: {e.stdout}, stderr:{e.stderr}")

    def _control_tasks(self, enable: bool):
        """Включает/отключает запланированные задачи."""
        action = "enable" if enable else "disable"
        for task in self.tasks:
            try:
                subprocess.run(["schtasks", "/change", "/tn", task, f"/{action}"], check=True, capture_output=True, text=True)
                self.log_action(f"_control_tasks ({task})", f"{action.capitalize()}d", True)
            except subprocess.CalledProcessError as e:
                self.log_action(f"_control_tasks ({task})", f"Failed to {action}", False)
                print(f"Error controlling task ({task}): {e}, stdout: {e.stdout}, stderr:{e.stderr}")
                # Не выходим, а продолжаем со следующей задачей

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "nvidia_telemetry_log.txt")
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