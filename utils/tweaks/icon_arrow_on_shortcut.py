import os
import winreg
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
import subprocess
import requests

class IconArrowOnShortcutTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Icons"
        self.value_name = "29"
        self.log_file = self.setup_log_file()
        #self.favicon_url = "https://git.io/blankfavicon16x16"  #  Устаревший URL
        self.favicon_url = "https://raw.githubusercontent.com/ALFiX01/blank-favicon/master/favicon.ico" #Актуальнй URL
        self.favicon_path = os.path.join(os.getenv('APPDATA'), "ASX-Hub", "Files", "Resources", "favicon.ico")


    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Стрелки на ярлыках",
            description="Включает/отключает отображение стрелок на ярлыках.",
            category="Кастомизация"
        )

    def check_status(self) -> bool:
        try:
            value = self.reg.get_registry_value(self.registry_path, self.value_name)
             # Если значение отсутствует или пустое, считаем, что стрелки отключены (False).
            return value is not None and value != ""
        except FileNotFoundError:
            # Если ключа "Shell Icons" нет, считаем, что стрелки отключены
            return False

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        try:
            # Удаляем значение 29, чтобы включить стрелки
            self.reg.delete_registry_value(self.registry_path, self.value_name, ignore_not_found=True)
            self.log_action("enable", "Enabled", True)
            self.restart_explorer()
            return True
        except Exception as e:
            print(f"Error enabling IconArrowOnShortcut: {e}")
            self.log_action("enable", "Enabled", False)
            return False

    def disable(self) -> bool:
         try:
            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(self.favicon_path), exist_ok=True)
            # Скачиваем пустую иконку
            #response = requests.get(self.favicon_url, stream=True) # закомментировал
            #response.raise_for_status() # закомментировал
            #with open(self.favicon_path, "wb") as f: # закомментировал
            #    for chunk in response.iter_content(chunk_size=8192): # закомментировал
            #        f.write(chunk) # закомментировал

            # Устанавливаем значение 29 на пустую строку или путь к иконке, чтобы отключить стрелки
            self.reg.set_registry_value(self.registry_path, self.value_name, "", winreg.REG_SZ)
            self.log_action("disable", "Disabled", True)
            self.restart_explorer()
            return True
         except (requests.exceptions.RequestException, Exception) as e: # OSError, requests.exceptions.RequestException, Exception) as e:
            print(f"Error disabling IconArrowOnShortcut: {e}")
            self.log_action("disable", "Disabled", False)
            return False

    def restart_explorer(self):
        """Перезапускает explorer.exe."""
        try:
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=True, shell=True)
            subprocess.run(["explorer.exe"], check=True, shell=True)
            self.log_action("restart_explorer", "Explorer restarted", True)
        except Exception as e:
            self.log_action("restart_explorer", f"Error restarting explorer: {e}", False)

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "icon_arrow_on_shortcut_log.txt")
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