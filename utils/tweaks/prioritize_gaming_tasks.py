import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class PrioritizeGamingTasksTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Приоритизация игровых задач",
            description="Включает/отключает повышенный приоритет для игровых задач",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        """
        Проверяет, включена ли приоритизация игровых задач.
        Приоритизация ВКЛЮЧЕНА, если Priority=6 и Scheduling Category=High.
        """
        try:
            priority = self.reg.get_registry_value(self.registry_path, "Priority")
            scheduling_category = self.reg.get_registry_value(self.registry_path, "Scheduling Category")
            # GPU Priority не проверяем, так как он одинаковый в обоих случаях

            status = (priority == 6 and scheduling_category == "High")  # True, если приоритизация включена
            self.log_action("check_status", f"Gaming Task Prioritization {'Enabled' if status else 'Disabled'}", True)
            return status
        except FileNotFoundError:
            # Если ключей нет, считаем, что приоритизация отключена (поведение по умолчанию).
            self.log_action("check_status", "Registry keys not found, assuming prioritization disabled", True)
            return False  # Приоритизация отключена
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Gaming Task Prioritization status: {e}")
            return False  # В случае ошибки считаем, что отключено


    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает приоритизацию игровых задач."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling Gaming Task Prioritization: {e}")
            return False

    def disable(self) -> bool:
        """Отключает приоритизацию игровых задач."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Gaming Task Prioritization: {e}")
            return False

    def _set_registry_values(self, enabled: bool):
        """Устанавливает значения реестра."""
        priority_value = 6 if enabled else 2
        scheduling_category_value = "High" if enabled else "Medium"
        gpu_priority_value = 8  # Всегда 8

        self.reg.set_registry_value(self.registry_path, "Priority", priority_value, winreg.REG_DWORD)
        self.reg.set_registry_value(self.registry_path, "Scheduling Category", scheduling_category_value, winreg.REG_SZ)
        self.reg.set_registry_value(self.registry_path, "GPU Priority", gpu_priority_value, winreg.REG_DWORD) # Всегда ставим


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "gaming_task_prioritization_log.txt")
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