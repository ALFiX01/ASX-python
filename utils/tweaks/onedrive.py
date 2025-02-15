import os
import subprocess
import winreg
import shutil
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class OneDriveTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()
        # Удаляем self.save_data_path и self.value_name, так как они больше не нужны для check_status

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Удаление OneDrive",
            description="Удаляет OneDrive и все связанные с ним компоненты",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        """
        Проверяет, установлен ли OneDrive.  Надежная проверка, не зависящая от нашего кастомного ключа в реестре.
        Возвращает True, если OneDrive установлен, False - если удален.
        """
        try:
            # 1. Проверяем, запущен ли процесс OneDrive.exe
            result = subprocess.run(["tasklist", "/fi", "ImageName eq OneDrive.exe", "/fo", "csv"], capture_output=True, text=True, check=False, creationflags=subprocess.CREATE_NO_WINDOW)
            if "OneDrive.exe" in result.stdout:
                self.log_action("check_status", "OneDrive process running", True)
                return True  # OneDrive запущен -> установлен

            # 2. Проверяем наличие установочного файла
            system32_path = os.path.join(os.getenv("SYSTEMROOT"), "System32", "OneDriveSetup.exe")
            syswow64_path = os.path.join(os.getenv("SYSTEMROOT"), "SysWOW64", "OneDriveSetup.exe")
            if os.path.exists(system32_path) or os.path.exists(syswow64_path):
                self.log_action("check_status", "OneDriveSetup.exe exists", True)
                return True  # Установщик есть -> вероятно, установлен

            # 3.  Проверяем наличие папки OneDrive в профиле пользователя
            user_profile = os.getenv("USERPROFILE")
            if user_profile:
                onedrive_path = os.path.join(user_profile, "OneDrive")
                if os.path.exists(onedrive_path) and not self._is_path_in_user_shell_folders(onedrive_path):
                    self.log_action("check_status", "OneDrive user folder exists", True)
                    return True  # Папка пользователя есть -> установлен

            # 4. Проверяем наличие ключей реестра, связанных с OneDrive (менее надежный способ, но все же)
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\OneDrive"):
                    self.log_action("check_status", "OneDrive registry key exists (HKCU)", True)
                    return True  # Ключ реестра OneDrive есть -> вероятно, установлен
            except FileNotFoundError:
                pass

            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\OneDrive"):
                    self.log_action("check_status", "OneDrive registry key exists (HKLM)", True)
                    return True # Ключ реестра OneDrive есть -> вероятно, установлен
            except FileNotFoundError:
                pass

            # Если ничего из вышеперечисленного не найдено, считаем, что OneDrive удален
            self.log_action("check_status", "OneDrive not found", False)
            return False

        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking OneDrive status: {e}")
            return False  # В случае ошибки считаем, что удален



    def remove(self) -> bool:
        """Удаляет OneDrive."""
        try:
            self.log_action("remove", "Attempting removal", False)

            self._kill_onedrive_process()
            self._remove_from_startup()
            self._uninstall_onedrive()
            self._remove_user_data()
            self._remove_installation_files()
            self._remove_shortcuts()
            self._disable_onedrive_usage()
            self._disable_automatic_installation()
            self._remove_folder_from_explorer()
            self._disable_scheduled_tasks()
            self._clear_environment_variable()
            # Больше не создаем ключ реестра при удалении!
            # self.reg.set_registry_value(self.save_data_path, self.value_name, 1, registry_type="REG_DWORD")


            self.log_action("remove", "Removed", True)
            return True
        except Exception as e:
            self.log_action("remove", "Removal failed", False)
            print(f"An unexpected error occurred during OneDrive removal: {e}")
            return False
    def enable(self) -> bool:
        """Заглушка для метода enable."""
        self.log_action("enable", "Not implemented", False)  # Логируем, что метод не реализован
        return False # Всегда False

    def disable(self) -> bool:
        """Заглушка для метода disable."""
        self.log_action("disable", "Not implemented", False) # Логируем, что метод не реализован
        return False  # Всегда False

    def toggle(self) -> bool:
        """Заглушка для метода toggle."""
        self.log_action("toggle", "Not implemented", False)  # Логируем, что метод не реализован
        return False # Всегда False

    def _kill_onedrive_process(self):
        """Завершает процесс OneDrive."""
        self.log_action("_kill_onedrive_process", "Attempting", False)
        try:
            subprocess.run(["taskkill", "/f", "/im", "OneDrive.exe"], check=False, capture_output=True, text=True)
            self.log_action("_kill_onedrive_process", "Killed", True)

        except subprocess.CalledProcessError as e:
            self.log_action("_kill_onedrive_process", "Failed to kill", False)
            print(f"Error killing OneDrive process: {e}")


    def _remove_from_startup(self):
        """Удаляет OneDrive из автозагрузки."""
        self.log_action("_remove_from_startup", "Attempting", False)
        try:
             self.reg.delete_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run", "OneDrive", ignore_not_found=True)
             self.log_action("_remove_from_startup", "Removed", True)
        except Exception as e:
            self.log_action("_remove_from_startup", "Failed to remove", False)
            print(f"Error removing OneDrive from startup: {e}")

    def _uninstall_onedrive(self):
        """Удаляет OneDrive через официальный установщик."""
        self.log_action("_uninstall_onedrive", "Attempting", False)
        system32_path = os.path.join(os.getenv("SYSTEMROOT"), "System32", "OneDriveSetup.exe")
        syswow64_path = os.path.join(os.getenv("SYSTEMROOT"), "SysWOW64", "OneDriveSetup.exe")

        if os.path.exists(system32_path):
            command = [system32_path, "/uninstall"]
        elif os.path.exists(syswow64_path):
            command = [syswow64_path, "/uninstall"]
        else:
            self.log_action("_uninstall_onedrive", "Installer not found", False)
            print("OneDriveSetup.exe not found.")
            return

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.log_action("_uninstall_onedrive", "Uninstalled", True)
        except subprocess.CalledProcessError as e:
            self.log_action("_uninstall_onedrive", "Failed to uninstall", False)
            print(f"Error uninstalling OneDrive: {e}")

    def _remove_user_data(self):
        """Удаляет пользовательские данные OneDrive."""
        self.log_action("_remove_user_data", "Attempting", False)
        user_profile = os.getenv("USERPROFILE")
        if not user_profile:
            print("USERPROFILE environment variable not found.")
            return

        onedrive_path = os.path.join(user_profile, "OneDrive")
        # Проверка нет ли в папке OneDrive других папок
        if os.path.exists(onedrive_path):
            try:
              if not self._is_path_in_user_shell_folders(onedrive_path):
                shutil.rmtree(onedrive_path, ignore_errors=True)  # Используем shutil.rmtree
                self.log_action("_remove_user_data", "Removed", True)
              else:
                  self.log_action("_remove_user_data", "OneDrive folder is used by the OS", False)
            except OSError as e:
                self.log_action("_remove_user_data", "Failed to remove", False)
                print(f"Error removing user data: {e}")
        else:
            self.log_action("_remove_user_data", "User data folder not found", True) # Папка уже отсутствует

    def _is_path_in_user_shell_folders(self, path_to_check):
        """Проверяет, не используется ли указанный путь в качестве папки оболочки пользователя."""
        user_shell_folders_path = r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                i = 0
                while True:
                    try:
                        value_name, value_data, _ = winreg.EnumValue(key, i)
                        expanded_path = os.path.expandvars(value_data)
                        if os.path.exists(expanded_path) and os.path.samefile(expanded_path, path_to_check):
                            return True  # Путь совпадает с одной из папок
                        i += 1
                    except OSError:
                        break  # Больше нет значений
        except FileNotFoundError:
            print("User Shell Folders registry key not found.")
        return False


    def _remove_installation_files(self):
        """Удаляет установочные файлы и кэш OneDrive."""
        self.log_action("_remove_installation_files", "Attempting", False)
        paths_to_remove = [
            os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "OneDrive"),
            os.path.join(os.getenv("PROGRAMDATA"), "Microsoft OneDrive"),
            os.path.join(os.getenv("SYSTEMDRIVE"), "OneDriveTemp"),
        ]

        for path in paths_to_remove:
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                         # Получаем права на запись для папки и её содержимого, если это необходимо
                        for root, dirs, files in os.walk(path):
                            for momo in dirs:
                                os.chmod(os.path.join(root, momo), 0o777)
                            for momo in files:
                                os.chmod(os.path.join(root, momo), 0o777)
                        shutil.rmtree(path, ignore_errors=False)
                    else:
                        os.remove(path)
                    self.log_action(f"_remove_installation_files ({path})", "Removed", True)
                except OSError as e:
                    self.log_action(f"_remove_installation_files ({path})", "Failed to remove", False)
                    print(f"Error removing installation files/cache ({path}): {e}")
            else:
               self.log_action(f"_remove_installation_files ({path})", "Not found", True) #Уже удален

    def _remove_shortcuts(self):
        """Удаляет ярлыки OneDrive."""
        self.log_action("_remove_shortcuts", "Attempting", False)
        shortcuts = [
            os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "OneDrive.lnk"),
            os.path.join(os.getenv("USERPROFILE"), "Links", "OneDrive.lnk"),
            os.path.join(os.getenv("SYSTEMROOT"), "ServiceProfiles", "LocalService", "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "OneDrive.lnk"),
            os.path.join(os.getenv("SYSTEMROOT"), "ServiceProfiles", "NetworkService", "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "OneDrive.lnk"),
        ]
        for shortcut in shortcuts:
            if os.path.exists(shortcut):
                try:
                    os.remove(shortcut)
                    self.log_action(f"_remove_shortcuts ({shortcut})", "Removed", True)
                except OSError as e:
                    self.log_action(f"_remove_shortcuts ({shortcut})", "Failed to remove", False)
                    print(f"Error removing shortcut ({shortcut}): {e}")
            else:
                self.log_action(f"_remove_shortcuts ({shortcut})", "Not Found", True) # Уже удален

        # Удаление из панели навигации проводника (Desktop\NameSpace)
        try:
            self.reg.delete_registry_key(r"HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Desktop\NameSpace\{018D5C66-4533-4307-9B53-224DE2ED1FE6}", ignore_not_found=True)
            self.log_action(f"_remove_shortcuts (namespace)", "Removed", True)
        except Exception as e:
             self.log_action(f"_remove_shortcuts (namespace)", "Failed", False)
             print(f"Failed to delete namespace key: {e}")


    def _disable_onedrive_usage(self):
        """Отключает использование OneDrive через групповые политики."""
        self.log_action("_disable_onedrive_usage", "Attempting", False)
        try:
            self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive", "DisableFileSyncNGSC", 1, winreg.REG_DWORD)
            self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive", "DisableFileSync", 1, winreg.REG_DWORD)
            self.log_action("_disable_onedrive_usage", "Disabled", True)
        except Exception as e:
            self.log_action("_disable_onedrive_usage", "Failed to disable", False)
            print(f"Error disabling OneDrive usage: {e}")

    def _disable_automatic_installation(self):
        """Отключает автоматическую установку OneDrive (для старых версий Windows)."""
        self.log_action("_disable_automatic_installation", "Attempting", False)

        # Проверка версии Windows (этот код, вероятно, не нужен на современных системах)
        try:
            version = subprocess.check_output(
                ["powershell", "-command", "[Environment]::OSVersion.Version | Select-Object -ExpandProperty Build"],
                text=True,
                creationflags = subprocess.CREATE_NO_WINDOW
            ).strip()
            build_number = int(version)
            if not (18363 <= build_number <= 19045):  # Диапазон версий
                self.log_action("_disable_automatic_installation", "Skipped (version check)", True)
                return

            self.reg.delete_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run", "OneDriveSetup", ignore_not_found=True)
            self.log_action("_disable_automatic_installation", "Disabled", True)
        except (subprocess.CalledProcessError, ValueError, Exception) as e:
            self.log_action("_disable_automatic_installation", "Failed or skipped", False)
            print(f"Error disabling automatic OneDrive installation: {e}")



    def _remove_folder_from_explorer(self):
        """Удаляет папку OneDrive из проводника."""
        self.log_action("_remove_folder_from_explorer", "Attempting", False)
        try:
            self.reg.set_registry_value(r"HKCU\Software\Classes\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}", "System.IsPinnedToNameSpaceTree", 0, winreg.REG_DWORD)
            self.reg.set_registry_value(r"HKCU\Software\Classes\Wow6432Node\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}", "System.IsPinnedToNameSpaceTree", 0, winreg.REG_DWORD)
            self.log_action("_remove_folder_from_explorer", "Removed", True)

        except Exception as e:
            self.log_action("_remove_folder_from_explorer", "Failed to remove", False)
            print(f"Error removing folder from Explorer: {e}")

    def _disable_scheduled_tasks(self):
        """Отключает запланированные задачи OneDrive."""
        self.log_action("_disable_scheduled_tasks", "Attempting", False)
        task_patterns = [
            "OneDrive Reporting Task-*",
            "OneDrive Standalone Update Task-*",
            "OneDrive Per-Machine Standalone Update",
        ]
        for pattern in task_patterns:
            try:
                # -Force для скрытых задач, -ErrorAction SilentlyContinue чтобы не вываливаться если задач нет
                subprocess.run(
                    ["powershell", "-command",
                     f"Get-ScheduledTask -TaskName '{pattern}' -ErrorAction SilentlyContinue | Disable-ScheduledTask -Confirm:$false -ErrorAction SilentlyContinue"],
                    check=False, capture_output=True, text=True
                )
                self.log_action(f"_disable_scheduled_tasks ({pattern})", "Disabled", True)

            except subprocess.CalledProcessError as e:
                self.log_action(f"_disable_scheduled_tasks ({pattern})", "Failed to disable", False)
                print(f"Error disabling scheduled tasks ({pattern}): {e}")

    def _clear_environment_variable(self):
        """Очищает переменную среды OneDrive."""
        self.log_action("_clear_environment_variable", "Attempting", False)
        try:
            self.reg.delete_registry_value(r"HKCU\Environment", "OneDrive", ignore_not_found=True)
            self.log_action("_clear_environment_variable", "Cleared", True)
        except Exception as e:
            self.log_action("_clear_environment_variable", "Failed to clear", False)
            print(f"Error clearing OneDrive environment variable: {e}")


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "onedrive_removal_log.txt") # Изменен лог файл
        return log_file

    def log_action(self, action, state, success):
        """Logs actions to the log file."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                if state != "Attempting":
                    print(log_message)  # Print to console too
        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp formatted for logging."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")