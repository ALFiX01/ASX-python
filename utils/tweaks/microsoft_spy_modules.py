import os
import winreg
import subprocess
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class MicrosoftSpyModulesTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()
        self.diagtrack_path = r"HKLM\SYSTEM\CurrentControlSet\Services\DiagTrack"
        self.dmwappushservice_path = r"HKLM\SYSTEM\CurrentControlSet\Services\dmwappushservice"

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Шпионские модули Microsoft",
            description="Отключает службы DiagTrack и dmwappushservice (потенциально)",
            category="Конфиденциальность",
            warning="Удаление ключей реестра служб может привести к нестабильной работе системы. Действуйте на свой страх и риск!"
        )
    def check_status(self) -> bool:
        """
        Проверяет, отключены ли шпионские модули (приблизительно).
        Считаем отключенными, если ключи реестра DiagTrack и dmwappushservice отсутствуют.
        Это не гарантирует полного отключения, но дает представление о состоянии.
        """
        try:
            # Проверяем наличие ключей.  Если их нет, значит, службы, скорее всего, удалены/отключены.
            self.reg.get_registry_value(self.diagtrack_path, "Start")  # Проверяем наличие ключа, значение не важно
            self.reg.get_registry_value(self.dmwappushservice_path, "Start")
            # Если оба ключа существуют, значит, службы, скорее всего, не удалены
            self.log_action("check_status", "Spy modules registry keys exist, assuming enabled", True)
            return False  # Считаем включенными
        except FileNotFoundError:
            # Если хотя бы одного ключа нет, считаем отключенными
            self.log_action("check_status", "One or more registry keys not found, assuming disabled", True)
            return True
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Microsoft Spy Modules status: {e}")
            return False # В случае ошибки


    def toggle(self) -> bool:
        current_status = self.check_status()
        # Если current_status == True (модули отключены), то ничего не делаем.
        if current_status:
            self.log_action("toggle", "Already disabled, skipping", False)
            print("Шпионские модули Microsoft уже отключены.")
            return False

        # Если current_status == False (модули включены), то отключаем
        return self.disable()

    def enable(self) -> bool:
        """
        Этот твик необратим (только отключает модули), поэтому enable не делает ничего.
        """
        self.log_action("enable", "Not applicable (irreversible tweak)", False)
        print("Включение шпионских модулей Microsoft невозможно.")
        return False

    def disable(self) -> bool:
        """Отключает (удаляет) шпионские модули Microsoft."""
        try:
            # Удаляем ключи реестра, связанные со службами.  Это *потенциально* опасно!
            self.reg.delete_registry_key(self.diagtrack_path, ignore_not_found=True)
            self.reg.delete_registry_key(self.dmwappushservice_path, ignore_not_found=True)

            self.log_action("disable", "Disabled (registry keys removed)", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling Microsoft Spy Modules: {e}")
            return False

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "microsoft_spy_modules_log.txt")
        return log_file
    def log_action(self, action, state, success):
        """Logs actions to the log file."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                if state != "Attempting" and "applicable" not in state:
                    print(log_message)  # Print to console too
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp formatted for logging."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")