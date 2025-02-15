import os
import winreg
from utils.tweaks.base_tweak import BaseTweak, TweakMetadata
from utils.registry_handler import RegistryHandler

class AppSettingsSyncTweak(BaseTweak):
    def __init__(self):
        self.reg = RegistryHandler()
        self.registry_path = r"HKLM\SOFTWARE\Policies\Microsoft\Windows\SettingSync"
        self.log_file = self.setup_log_file()
        # Список ключей и их значений по умолчанию (для включения синхронизации)
        self.settings = {
            "DisableApplicationSettingSync": 0,
            "DisableWebBrowserSettingSync": 0,
            "DisableDesktopThemeSettingSync": 0,
            "DisableSettingSync": 0,
            "DisableSyncOnPaidNetwork": 0,  # Этот ключ отличается!
            "DisableWindowsSettingSync": 0,
            "DisableCredentialsSettingSync": 0,
            "DisablePersonalizationSettingSync": 0,
            "DisableStartLayoutSettingSync": 0,
        }

    @property
    def metadata(self) -> TweakMetadata:
        return TweakMetadata(
            title="Синхронизация настроек приложений",
            description="Включает/отключает синхронизацию настроек приложений и Windows",
            category="Конфиденциальность"
        )
    def check_status(self) -> bool:
        """
        Проверяет, включена ли синхронизация настроек приложений.
        Синхронизация ВКЛЮЧЕНА, если ВСЕ ключи имеют значения по умолчанию (0 или 1 для DisableSyncOnPaidNetwork).
        Если хотя бы одного ключа нет, считаем, что синхронизация *отключена*.
        """
        try:
            all_enabled = True
            for key, default_value in self.settings.items():
                value = self.reg.get_registry_value(self.registry_path, key)
                # Особая обработка для DisableSyncOnPaidNetwork
                if key == "DisableSyncOnPaidNetwork":
                  if value != (1 if default_value == 0 else 0): # инвертируем
                      all_enabled = False
                      break
                elif value != default_value:
                    all_enabled = False
                    break

            self.log_action("check_status", f"App Settings Sync {'Enabled' if all_enabled else 'Disabled'}", True)
            return all_enabled  # True, если синхронизация включена

        except FileNotFoundError:
            # Если какого-то ключа нет, считаем, что синхр. *отключена*.
            self.log_action("check_status", "One or more registry keys not found, assuming disabled", True)
            return False  # Отключена
        except Exception as e:
            self.log_action("check_status", f"Error checking status: {e}", False)
            print(f"Error checking App Settings Sync status: {e}")
            return False  # В случае ошибки

    def toggle(self) -> bool:
        current_status = self.check_status()
        result = self.disable() if current_status else self.enable()
        self.log_action("toggle", "Disabled" if current_status else "Enabled", result)
        return result

    def enable(self) -> bool:
        """Включает синхронизацию настроек приложений."""
        try:
            self._set_registry_values(enabled=True)
            self.log_action("enable", "Enabled", True)
            return True
        except Exception as e:
            self.log_action("enable", "Failed to enable", False)
            print(f"Error enabling App Settings Sync: {e}")
            return False

    def disable(self) -> bool:
        """Отключает синхронизацию настроек приложений."""
        try:
            self._set_registry_values(enabled=False)
            self.log_action("disable", "Disabled", True)
            return True
        except Exception as e:
            self.log_action("disable", "Failed to disable", False)
            print(f"Error disabling App Settings Sync: {e}")
            return False


    def _set_registry_values(self, enabled: bool):
      """Устанавливает значения реестра."""
      for key, default_value in self.settings.items():
          # Особая обработка для DisableSyncOnPaidNetwork
          if key == "DisableSyncOnPaidNetwork":
              value = 1 if not enabled else 0
              self.reg.set_registry_value(self.registry_path, key, value, winreg.REG_DWORD)
          else:
              # Для всех остальных ключей: 2 - отключить, 0 - включить (или значение по умолчанию)
              value = 2 if not enabled else default_value
              self.reg.set_registry_value(self.registry_path, key, value, winreg.REG_DWORD)


    def setup_log_file(self):
        """Sets up the log file path, creating directories if necessary."""
        app_data_dir = os.getenv('APPDATA')
        if not app_data_dir:
            app_data_dir = os.path.expanduser("~")
        log_dir = os.path.join(app_data_dir, "ASX-Hub", "Logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app_settings_sync_log.txt")
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