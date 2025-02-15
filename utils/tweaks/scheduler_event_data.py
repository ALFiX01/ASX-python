import os
import subprocess
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class SchedulerEventDataTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()
        self.save_data_path = os.path.join(os.getenv('APPDATA'), "ASX-Hub", "SaveData", "ParameterFunction")
        self.value_name = "SchedulerEventData"
        # Запланированные задачи
        self.tasks = [
            r"Microsoft\Windows\Maintenance\WinSAT",
            r"Microsoft\Windows\Autochk\Proxy",
            r"Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
            r"Microsoft\Windows\Application Experience\ProgramDataUpdater",
            r"Microsoft\Windows\Application Experience\StartupAppTask",
            r"Microsoft\Windows\PI\Sqm-Tasks",
            r"Microsoft\Windows\NetTrace\GatherNetworkInfo",
            r"Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
            r"Microsoft\Windows\Customer Experience Improvement Program\KernelCeipTask",
            r"Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
            r"Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticResolver",
            r"Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector",
        ]
        # Определение кодировки OEM, как и в предыдущем примере с телеметрией
        try:
            self.oem_encoding = 'cp' + subprocess.check_output('chcp', shell=True, text=True).split(':')[-1].strip()
        except (subprocess.CalledProcessError, ValueError):
            self.oem_encoding = 'cp866'
            print(f"Warning: Could not determine OEM codepage.  Using default: {self.oem_encoding}")


    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Сбор данных планировщика",
            description="Включает/отключает сбор данных через события планировщика задач",
            category="Конфиденциальность"  # Твик конфиденциальности
        )

    def check_status(self) -> bool:
        """
        Проверяет, включен ли сбор данных (приблизительно).
        Использует наличие ключа в реестре который мы создаем.
        """
        value = self.reg.get_registry_value(self.save_data_path, self.value_name)
        status = value is None  # True - сбор включен (нет ключа), False - сбор отключен (ключ есть)
        self.log_action("check_status", f"Scheduler Event Data Collection {'Enabled' if status else 'Disabled'}", True)
        return status  # True если сбор включен


    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает сбор данных через события планировщика."""
        try:
            # self.reg.set_registry_value(self.save_data_path, self.value_name, 0, registry_type="REG_SZ") #Удаляем создание ключа
            self._set_scheduled_tasks(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Scheduler Event Data Collection: {e}")
            return False

    def disable(self) -> bool:
        """Отключает сбор данных через события планировщика."""
        try:
            # self.reg.delete_registry_value(self.save_data_path, self.value_name, ignore_not_found=True) #Удаляем
            self._set_scheduled_tasks(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Scheduler Event Data Collection: {e}")
            return False

    def _set_scheduled_tasks(self, enabled: bool):
        """Включает/отключает запланированные задачи."""
        action = "enable" if enabled else "disable"
        for task in self.tasks:
            try:
                subprocess.run(["schtasks", "/change", "/tn", task, f"/{action}"], check=True, capture_output=True,
                               text=True, encoding=self.oem_encoding)
                self.log_action(f"_set_scheduled_tasks ({task})", f"{action.capitalize()}d", True)
            except subprocess.CalledProcessError as e:
                # Игнорируем ошибку, если задача не найдена
                if "ERROR: The system cannot find the file specified" in e.stderr or "ОШИБКА: указанное имя задачи" in e.stderr:  # Добавили проверку на русскоязычную ошибку
                    self.log_action(f"_set_scheduled_tasks ({task})", f"Task not found, skipping", False)
                    print(f"Warning: Scheduled task '{task}' not found. Skipping.")
                else:
                    self.log_action(f"_set_scheduled_tasks ({task})", f"Failed to {action}", False)
                    print(f"Error controlling task ({task}): {e}, stdout:{e.stdout}, stderr: {e.stderr}")


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "scheduler_event_data_log.txt")
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