# Код для utils/tweaks/widgets_uninstall.py (с измененным check_status)

import os
import subprocess
import winreg
import shutil
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class WidgetsUninstallTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.log_file = self.setup_log_file()
        # Удаляем self.save_data_path и self.value_name

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Удаление виджетов Windows",
            description="Удаляет компоненты виджетов Windows (Web Experience Pack)",
            category="Оптимизация и настройки"
        )

    def check_status(self) -> bool:
        """
        Проверяет, удалены ли виджеты.  Более надежная проверка.
        Возвращает True, если виджеты УДАЛЕНЫ, False - если установлены.
        """
        try:
            # 1. Проверяем наличие TaskbarDa = 0 в реестре
            taskbar_da_value = self.reg.get_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarDa")
            if taskbar_da_value == 0:
                self.log_action("check_status", "TaskbarDa is 0, likely uninstalled", False)
                # return True  # Если TaskbarDa = 0, считаем, что удалены.  Но продолжаем проверки!

            # 2. Проверяем наличие папки WindowsApps и Widgets.dll
            program_files = os.getenv("ProgramFiles")
            if program_files:
                windows_apps_path = os.path.join(program_files, "WindowsApps")
                if os.path.exists(windows_apps_path):
                    widgets_dll_found = False
                    for root, dirs, files in os.walk(windows_apps_path):
                        if "Widgets.dll" in files:
                            widgets_dll_found = True
                            break  # Выходим из цикла, если нашли
                    if widgets_dll_found:
                        self.log_action("check_status", "Widgets.dll found, likely installed", False)
                        return False # Если нашли Widgets.dll, то не удалены
                else:
                    self.log_action("check_status", "WindowsApps folder not found", False)
                    #return True # Папка WindowsApps не найдена, считаем, что удалено. Но продолжаем проверки
            else:
                self.log_action("check_status", "ProgramFiles env var not found", False)
                #return True  # Не можем проверить, считаем, что не удалены, продолжаем проверки.

            # 3. Проверяем, удалены ли Appx-пакеты (менее надежный способ, но все же)
            packages = [
                "*DesktopPackageMetadata*",
                "*MicrosoftWindows.Client.WebExperience*",
                "*Microsoft.WidgetsPlatformRuntime*",
                "*WebExperience*",
                "*WidgetServicePackage*",
            ]
            all_packages_removed = True
            for package in packages:
                try:
                    result = subprocess.run(
                        ["powershell", "-Command", f"Get-AppxPackage {package}"],
                        check=False,
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:  # Если вывод не пустой, значит пакет найден
                        all_packages_removed = False
                        self.log_action("check_status", f"Appx package {package} found", False)
                        break  # Выходим из цикла, если нашли хотя бы один пакет
                except subprocess.CalledProcessError as e:
                    print(f"Error checking Appx package ({package}): {e}")
                    # Если ошибка при проверке, считаем, что пакет присутствует (для надежности)
                    all_packages_removed = False
                    break
            if all_packages_removed:
               self.log_action("check_status", "Appx packages not found, likely uninstalled", False)
            else:
                return False # Если хоть один пакет есть, то не удалено

            # Проверяем наличие ключа в реестре.
            value = self.reg.get_registry_value(r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Appx\AppxAllUserStore\Deprovisioned\MicrosoftWindows.Client.WebExperience_cw5n1h2txyewy",
            "(Default)")
            if value is not None:
                return False

            # Если все проверки указывают на удаление, считаем, что виджеты удалены
            self.log_action("check_status", "Widgets likely uninstalled", True)
            return True

        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking Widgets status: {e}")
            return False  # В случае ошибки считаем, что НЕ удалены


    def toggle(self) -> bool:
        # Этот твик - однонаправленное действие (только удаление).  Поэтому toggle вызывает uninstall.
        self.log_action("toggle", "Uninstalling", False)  # Лог, что toggle вызвал uninstall
        return self.uninstall()

    def enable(self) -> bool:
        self.log_action("enable", "Not applicable", False)  # Лог
        return False

    def disable(self) -> bool:
        self.log_action("disable", "Not applicable", False)   # Лог
        return False


    def uninstall(self) -> bool:
        """Удаляет виджеты Windows."""
        try:
            self.log_action("uninstall", "Attempting removal", False)

            self._remove_appx_packages()
            self._set_registry_keys()
            self._remove_widgets_folder()

            self.log_action("uninstall", "Removed", True)
            return True
        except Exception as e:
            self.log_action("uninstall", "Removal failed", False)
            print(f"An unexpected error occurred during Widgets removal: {e}")
            return False

    def _remove_appx_packages(self):
        """Удаляет Appx-пакеты, связанные с виджетами."""
        self.log_action("_remove_appx_packages", "Attempting", False)
        packages = [
            "*DesktopPackageMetadata*",
            "*MicrosoftWindows.Client.WebExperience*",
            "*Microsoft.WidgetsPlatformRuntime*",
            "*WebExperience*",
            "*WidgetServicePackage*",
        ]
        for package in packages:
            try:
                subprocess.run(
                    ["powershell", "-Command", f"Get-AppxPackage {package} | Remove-AppxPackage"],
                    check=False,  # Не выходим, если пакета нет
                    capture_output=True,
                    text=True
                )
                self.log_action(f"_remove_appx_packages ({package})", "Removed", True)
            except subprocess.CalledProcessError as e:
                self.log_action(f"_remove_appx_packages ({package})", "Failed to remove", False)
                print(f"Error removing Appx package ({package}): {e}")

    def _set_registry_keys(self):
        """Устанавливает/удаляет ключи реестра."""
        self.log_action("_set_registry_keys", "Attempting", False)
        try:
            # Отключение виджетов на панели задач
            self.reg.set_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarDa", 0, winreg.REG_DWORD)
            self.reg.set_registry_value(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowTaskViewButton", 0, winreg.REG_DWORD)

            # Отключение "Новостей и интересов"
            self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Dsh", "AllowNewsAndInterests", 0, winreg.REG_DWORD)
            self.reg.set_registry_value(r"HKLM\SOFTWARE\Microsoft\PolicyManager\default\NewsAndInterests\AllowNewsAndInterests", "value", 0, winreg.REG_DWORD)
            self.reg.set_registry_value(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Feeds", "EnableFeeds", 0, winreg.REG_DWORD)
            # Деактивация Web Experience
            self.reg.set_registry_value(r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Appx\AppxAllUserStore\Deprovisioned\MicrosoftWindows.Client.WebExperience_cw5n1h2txyewy",
                                         "(Default)",  # Устанавливаем значение по умолчанию
                                        "",  # Пустая строка
                                        winreg.REG_SZ)

            self.log_action("_set_registry_keys", "Keys set/removed", True)


        except Exception as e:
            self.log_action("_set_registry_keys", "Failed to set/remove keys", False)
            print(f"Error setting registry keys: {e}")

    def _remove_widgets_folder(self):
        """Удаляет папку Widgets.dll (если найдена)."""
        self.log_action("_remove_widgets_folder", "Attempting", False)
        program_files = os.getenv("ProgramFiles")
        if not program_files:
            print("ProgramFiles environment variable not found.")
            return
        windows_apps_path = os.path.join(program_files, "WindowsApps")

        if not os.path.exists(windows_apps_path):
            print("WindowsApps folder not found.")
            return

        for root, dirs, files in os.walk(windows_apps_path):
            for file in files:
                if file == "Widgets.dll":
                    widgets_path = os.path.join(root, file)
                    # Обрезаем widgets_path до папки
                    widgets_path = os.path.dirname(widgets_path)
                    self.log_action("_remove_widgets_folder", f"Widgets.dll found in: {widgets_path}", False)
                    try:
                        # Получаем права на папку и её содержимое
                        subprocess.run(["takeown", "/f", widgets_path, "/r", "/d", "y"], check=True, capture_output=True, text=True)
                        subprocess.run(["icacls", widgets_path, "/grant", f"{os.getlogin()}:F", "/t"], check=True, capture_output=True, text=True)
                        # Удаляем папку (рекурсивно)
                        shutil.rmtree(widgets_path, ignore_errors=False)
                        self.log_action("_remove_widgets_folder", f"Removed {widgets_path}", True)
                    except (subprocess.CalledProcessError, OSError) as e:
                        self.log_action("_remove_widgets_folder", f"Failed to remove {widgets_path}", False)
                        print(f"Error removing Widgets folder ({widgets_path}): {e}")
                    return  # Выходим из цикла, если нашли и удалили


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "widgets_uninstall_log.txt")
        return log_file

    def log_action(self, action, state, success):
        """Logs actions to the log file."""
        try:
            with open(self.log_file, "a") as f:
                timestamp = self.get_timestamp()
                log_message = f"[{timestamp}] Action: {action}, State: {state}, Success: {success}\n"
                f.write(log_message)
                if state != "Attempting" and "changed" not in state and "applicable" not in state:
                    print(log_message)  # Print to console too

        except Exception as e:
            print(f"Error writing to log file: {e}")

    def get_timestamp(self):
        """Gets the current timestamp formatted for logging."""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")