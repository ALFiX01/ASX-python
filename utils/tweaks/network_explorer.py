import os
import winreg
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
import subprocess

class NetworkExplorerTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = "HKCU\\Software\\Classes\\CLSID\\{F02C1A0D-BE21-4350-88B0-7367FC96EF3C}"
        self.value_name = "System.IsPinnedToNameSpaceTree"
        self.log_file = self.setup_log_file()

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Сеть в проводнике",
            description="Включает/отключает отображение 'Сеть' в панели навигации проводника.",
            category="Кастомизация"
        )

    def check_status(self) -> bool:
        # Продвинутая проверка статуса: проверяем и реестр, и наличие иконки в проводнике
        reg_value = self.reg.get_registry_value(self.registry_path, self.value_name)

        # Если в реестре отключено (0 или None), то точно отключено
        if reg_value != 1:
            return False

        # Если в реестре включено (1), проверяем наличие иконки в проводнике
        try:
            # Используем PowerShell для проверки, виден ли элемент "Network" в Namespace
            #  Эта команда PowerShell проверяет наличие элемента Network в пространстве имен проводника.
            command = 'powershell -Command "[bool]((New-Object -ComObject Shell.Application).Namespace(\'::{F02C1A0D-BE21-4350-88B0-7367FC96EF3C}\').Self.Name)"'
            result = subprocess.run(command, capture_output=True, text=True, shell=True, check=True) #Добавил , shell=True
            # Если команда выполнилась успешно и вернула "True", значит, иконка видна.
            return result.stdout.strip().lower() == 'true'

        except (subprocess.CalledProcessError, FileNotFoundError, Exception):
            # Если произошла ошибка при выполнении PowerShell (например, PowerShell не установлен),
            # считаем, что иконка не видна (на всякий случай лучше вернуть False)
            return False
    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 1, winreg.REG_DWORD)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            print(f"Error enabling NetworkExplorer: {e}")
            self.log_action("enable", "Enabled", False)
            return False

    def disable(self) -> bool:
        try:
            self.reg.set_registry_value(self.registry_path, self.value_name, 0, winreg.REG_DWORD)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            print(f"Error disabling NetworkExplorer: {e}")
            self.log_action("disable", "Disabled", False)
            return False

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "network_explorer_log.txt")
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