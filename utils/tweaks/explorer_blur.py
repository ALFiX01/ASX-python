import os
import subprocess
import requests
import zipfile
import winreg
from utils.registry_handler import RegistryHandler
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata

class ExplorerBlurTweak(BaseTweak):
    def __init__(self):
        self.asx_directory = os.getenv('APPDATA') + "\\ASX-Hub" #Пример
        self.resource_dir = os.path.join(self.asx_directory, "Files", "Resources", "AcrylicExplorer")
        self.dll_path = os.path.join(self.resource_dir, "ExplorerBlurMica.dll")
        self.zip_url = "https://github.com/ALFiX01/ASX-Hub/releases/download/File/AcrylicExplorer.zip"
        self.zip_path = os.path.join(self.asx_directory, "Files", "Resources", "AcrylicExplorer.zip")
        self.save_data_key = "HKCU\\Software\\ASX-Hub\\ParameterFunction"  #  Используем полный путь с HKCU
        self.value_name = "AcrylicExplorer"
        self.log_file = self.setup_log_file()
        self.reg = RegistryHandler()  #  Не передаём HKEY

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Размытие фона проводника",
            description="Включает/отключает размытие фона в проводнике Windows.",
            category="Оптимизация и настройки"
        )
    def check_status(self) -> bool:
        try:
            value = self.reg.get_registry_value(self.save_data_key, self.value_name) # Убрали HKEY
            if value == "0":
                return True
            return False
        except FileNotFoundError:
            return False

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if not current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        try:
            # Создаём все директории
            os.makedirs(os.path.dirname(self.zip_path), exist_ok=True)

            # Скачиваем ZIP-архив
            response = requests.get(self.zip_url, stream=True)
            response.raise_for_status()  # Проверяем статус ответа
            with open(self.zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Распаковываем архив
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.resource_dir)

            # Удаляем ZIP-архив
            os.remove(self.zip_path)

            # Регистрируем DLL
            subprocess.run(["regsvr32", self.dll_path], check=True, shell = True)
            #subprocess.run(["regsvr32", self.dll_path], check=True, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Записываем в реестр
            self.reg.set_registry_value(self.save_data_key, self.value_name, "0", winreg.REG_SZ) # Убрали HKEY

            self.log_action("enable", "Enabled", True)
            return True

        except (requests.exceptions.RequestException, zipfile.BadZipFile, subprocess.CalledProcessError, OSError, Exception) as e:
            self.log_action("enable", "Enabled", False)
            print(f"Error enabling Explorer Blur: {e}")
            return False
    def disable(self) -> bool:
        try:
            # Снимаем регистрацию DLL
            #subprocess.run(["regsvr32", "/u", self.dll_path], check=True, shell = True)
            subprocess.run(["regsvr32", "/u", self.dll_path], check=True, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Перезапускаем explorer.exe
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=True, shell = True)
            subprocess.run(["explorer.exe"], check=True, shell = True)


            # Удаляем папку AcrylicExplorer
            if os.path.exists(self.resource_dir):
                for root, dirs, files in os.walk(self.resource_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(self.resource_dir)


            # Удаляем запись из реестра
            self.reg.delete_registry_value(self.save_data_key, self.value_name) # Убрали HKEY
            self.log_action("disable", "Disabled", True)
            return True

        except (subprocess.CalledProcessError, OSError, FileNotFoundError, Exception) as e:
            print(f"Error disabling Explorer Blur: {e}")
            self.log_action("disable", "Disabled", False)
            return False

    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "explorer_blur_log.txt")
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