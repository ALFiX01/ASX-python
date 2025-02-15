import os
import subprocess
import winreg  # Используем winreg для работы с реестром
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler


class IndexingTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\WSearch"
        self.value_name = "Start"
        self.log_file = self.setup_log_file()
        self.service_name = "WSearch"

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Индексирование",
            description="Включает/отключает службу Windows Search (индексирование)",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        """
        Проверяет статус службы индексирования.
        Если значение Start равно 4, служба отключена (возвращаем False).
        Иначе служба включена (возвращаем True).
        """
        try:
            value = self.reg.get_registry_value(self.registry_path, self.value_name)
            return value != 4
        except FileNotFoundError:
            # Если ключа нет, считаем, что служба в состоянии по умолчанию (включена)
            return True
        except Exception as e:
            print(f"Error checking indexing status: {e}")
            return True  # В случае ошибки считаем, что включено


    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if not current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает службу индексирования."""
        try:
            # Устанавливаем значение Start в 2 (Automatic)
            self.reg.set_registry_value(self.registry_path, self.value_name, 2, winreg.REG_DWORD)

            # Настраиваем автозапуск службы
            subprocess.run(["sc", "config", self.service_name, "start=", "auto"], check=True, capture_output=True, text=True)
            # Запускаем службу
            subprocess.run(["net", "start", self.service_name], check=True, capture_output=True, text=True)
            self.log_action("enable", "Enabled", True)
            return True
        except subprocess.CalledProcessError as e:
            self.log_action("enable", "Enabled", False)
            print(f"Error enabling indexing: {e}")
            print(f"  stdout: {e.stdout}")
            print(f"  stderr: {e.stderr}")
            return False
        except Exception as e:
            self.log_action("enable", "Enabled", False)
            print(f"An unexpected error occurred: {e}")
            return False
    def disable(self) -> bool:
        """Отключает службу индексирования."""
        try:
            # Устанавливаем значение Start в 4 (Disabled)
            self.reg.set_registry_value(self.registry_path, self.value_name, 4, winreg.REG_DWORD)
            # Настраиваем службу на отключение
            subprocess.run(["sc", "config", self.service_name, "start=", "disabled"], check=True, capture_output=True, text=True)

            # Останавливаем службу.  Добавлена обработка случая, когда служба уже остановлена.
            try:
                subprocess.run(["net", "stop", self.service_name], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                if "The service has not been started" not in e.stderr:
                    raise  # Если ошибка не связана с тем, что служба уже остановлена, перевыбрасываем исключение

            self.log_action("disable", "Disabled", True)
            return True
        except subprocess.CalledProcessError as e:
            self.log_action("disable", "Disabled", False)
            print(f"Error disabling indexing: {e}")
            print(f"  stdout: {e.stdout}")
            print(f"  stderr: {e.stderr}")
            return False
        except Exception as e:
            self.log_action("disable", "Disabled", False)
            print(f"An unexpected error occurred: {e}")
            return False


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "indexing_log.txt")
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