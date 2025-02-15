import os
import subprocess
import requests  # Добавляем requests
import shutil  # Для копирования файла hosts
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler  #  Может пригодиться в будущем

class DataDomainsTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()  #  Может пригодиться в будущем
        self.log_file = self.setup_log_file()
        self.hosts_url = "https://github.com/ALFiX01/ASX-Hub/raw/main/Files/Other/hosts.txt"  # URL файла hosts
        self.hosts_local_path = os.path.join(os.getenv('APPDATA'), "ASX-Hub", "Files", "Resources", "host.txt")
        self.system_hosts_path = r"C:\Windows\System32\drivers\etc\hosts"  # Путь к системному файлу hosts
        self.restore_dir = os.path.join(os.getenv('APPDATA'), "ASX-Hub", "Files", "Restore")
        self.backup_file = os.path.join(self.restore_dir, "hosts_backup")
        self.save_data_path = os.path.join(os.getenv('APPDATA'), "ASX-Hub", "SaveData", "ParameterFunction") # путь к реестру
        self.value_name = "DataDomains"


    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Блокировка доменов (hosts)",
            description="Помогает блокировать домены сбора данных, рекламы и т.д. путем редактирования файла hosts.",
            category="Оптимизация и настройки",  #  Или "Безопасность", если считаете более подходящим
            #  Предупреждение о потенциальных рисках
            warning="Изменение файла hosts может привести к проблемам с доступом к некоторым сайтам.  Будьте осторожны!"
        )

    def check_status(self) -> bool:
        """
        Проверяет, был ли применен твик (приблизительно). Т.к мы отметили его в реестре.
        """
        value = self.reg.get_registry_value(self.save_data_path, self.value_name)
        status = value is not None  # True - была попытка добавления записей, False - не была
        self.log_action("check_status", f"Hosts file modification {'attempted' if status else 'not attempted'}", True)
        return status

    def toggle(self) -> bool:
      current_status = self.check_status()
      if not current_status:  # Если статус "не был применен"
        return self.modify()
      else:
        self.log_action("toggle", "Already modified, skipping.", False)
        print("Действие уже было выполнено. Повторное выполнение невозможно.")
        return False


    def enable(self):
      self.log_action("enable", "Not applicable", False)
      return False

    def disable(self):
      self.log_action("disable", "Not applicable", False)
      return False


    def modify(self) -> bool:
        """Скачивает файл hosts, делает резервную копию системного hosts, и открывает оба файла в Блокноте."""
        try:
            self.log_action("modify", "Attempting to modify hosts file", False)

            # 1. Скачиваем файл hosts
            if not self._download_hosts_file():
                return False  # Если не удалось скачать, выходим

            # 2. Делаем резервную копию системного файла hosts
            if not self._backup_system_hosts():
                return False  # Если не удалось сделать резервную копию, выходим


            # 3. Открываем оба файла в Блокноте для ручного редактирования
            try:
                subprocess.Popen(["notepad.exe", self.hosts_local_path])
                subprocess.Popen(["notepad.exe", self.system_hosts_path])
                self.log_action("modify", "Opened hosts files in Notepad", True)
            except Exception as e:
                self.log_action("modify", "Failed to open hosts files in Notepad", False)
                print(f"Error opening hosts files: {e}")
                return False

            # Предупреждение пользователю
            print("\nВНИМАНИЕ: Редактирование файла hosts может привести к неработоспособности некоторых сайтов.")
            print("Скопируйте нужные строки из скачанного файла hosts.txt в системный файл hosts.")
            print("Будьте предельно осторожны и сохраняйте изменения в системном файле hosts только если вы понимаете, что делаете!\n")
            self.reg.set_registry_value(self.save_data_path, self.value_name, 1, registry_type="REG_SZ")
            return True

        except Exception as e:
            self.log_action("modify", "Failed to modify hosts file", False)
            print(f"An unexpected error occurred: {e}")
            return False

    def _download_hosts_file(self) -> bool:
        """Скачивает файл hosts.txt."""
        try:
            response = requests.get(self.hosts_url, stream=True)
            response.raise_for_status()  # Проверяем статус HTTP (200 OK)

            # Создаем директории, если их нет
            os.makedirs(os.path.dirname(self.hosts_local_path), exist_ok=True)

            with open(self.hosts_local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self.log_action("_download_hosts_file", f"Downloaded hosts file to {self.hosts_local_path}", True)
            return True

        except requests.exceptions.RequestException as e:
            self.log_action("_download_hosts_file", f"Failed to download hosts file: {e}", False)
            print(f"Error downloading hosts file: {e}")
            return False
        except Exception as e:
            self.log_action("_download_hosts_file", f"Failed to download hosts file: {e}", False)
            print(f"Error downloading hosts file: {e}")
            return False


    def _backup_system_hosts(self) -> bool:
        """Делает резервную копию системного файла hosts."""
        try:
            os.makedirs(self.restore_dir, exist_ok=True)  # Создаем директорию Restore, если ее нет
            shutil.copy2(self.system_hosts_path, self.backup_file)  # Копируем с метаданными
            self.log_action("_backup_system_hosts", f"Backed up system hosts file to {self.backup_file}", True)
            return True
        except Exception as e:
            self.log_action("_backup_system_hosts", f"Failed to backup system hosts file: {e}", False)
            print(f"Error backing up hosts file: {e}")
            return False
    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "data_domains_log.txt")
        return log_file

    def log_action(self, action, state, success):
        """Logs actions to the log file."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                if (state != "Attempting") and ("Not applicable" not in state) :
                    print(log_message)
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp formatted for logging."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")